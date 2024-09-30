import pandas as pd
import numpy as np
import json
import os
from multiprocessing import Pool
from tqdm.notebook import tqdm
import gc
import pickle
import joblib
import cv2
import bz2
from PIL import Image
import matplotlib.pyplot as plt
import time

import sys
import numpy as np
np.set_printoptions(threshold=sys.maxsize)

REDUCE_MEM = True
MODEL_FILE_DIR = 'C:/closed/test/imaterialist2020-pretrain-models/'
attr_image_size = (160,160)

train_df = pd.read_csv("C:/closed/test/imaterialist-fashion-2020-fgvc7/train.csv")

to_training = not os.path.isfile(MODEL_FILE_DIR+"maskmodel_%d.model"%attr_image_size[0])

def rle_to_mask(rle_string,height,width):
    rows, cols = height, width
    if rle_string == -1:
        return np.zeros((height, width))
    else:
        rleNumbers = [int(numstring) for numstring in rle_string.split(' ')]
        rlePairs = np.array(rleNumbers).reshape(-1,2)
        img = np.zeros(rows*cols,dtype=np.uint8)
        for index,length in rlePairs:
            index -= 1
            img[index:index+length] = 255
        img = img.reshape(cols,rows)
        img = img.T
        return img

def mask_to_rle(mask):
    pixels = mask.T.flatten()
    # We need to allow for cases where there is a '1' at either end of the sequence.
    # We do this by padding with a zero at each end when needed.
    use_padding = False
    if pixels[0] or pixels[-1]:
        use_padding = True
        pixel_padded = np.zeros([len(pixels) + 2], dtype=pixels.dtype)
        pixel_padded[1:-1] = pixels
        pixels = pixel_padded
    rle = np.where(pixels[1:] != pixels[:-1])[0] + 2
    if use_padding:
        rle = rle - 1
    rle[1::2] = rle[1::2] - rle[:-1:2]
    return ' '.join(str(x) for x in rle)

def ptoz(obj):
    return bz2.compress(pickle.dumps(obj), 3) if REDUCE_MEM else obj
def ztop(b):
    return pickle.loads(bz2.decompress(b)) if REDUCE_MEM else b
def __getitem__(imgid):
    df = train_df[train_df.ImageId==imgid]
    res = []
    imag = cv2.imread("C:/closed/test/imaterialist-fashion-2020-fgvc7/train/"+str(imgid)+".jpg")
    for idx in range(len(df)):
        t = df.values[idx]
        cid = t[4]
        mask = rle_to_mask(t[1],t[2],t[3])
        attr = map(int,str(t[5]).split(",")) if str(t[5]) != 'nan' else []
        where = np.where(mask != 0)
        y1,y2,x1,x2 = 0,0,0,0
        if len(where[0]) > 0 and len(where[1]) > 0:
            y1,y2,x1,x2 = min(where[0]),max(where[0]),min(where[1]),max(where[1])
        if y2>y1+10 and x2>x1+10:
            X = cv2.resize(imag[y1:y2,x1:x2], attr_image_size)
            X = ptoz(X)
        else:
            X = None
        mask = cv2.resize(mask, attr_image_size)
        mask = ptoz(mask)
        res.append((cid, mask, attr, X))
    imag = cv2.resize(imag, attr_image_size)
    imag = ptoz(imag)
    return res, imag, imgid

import torch
import torch.nn as nn
import torch.nn.functional as F

@torch.jit.script
def mish(input):
    return input * torch.tanh(F.softplus(input))

class Mish(nn.Module):
    def __init__(self):
        super().__init__()

    def forward(self, input):
        return mish(input)

class SeparableConv2d(nn.Module):
    def __init__(self,in_channels,out_channels,kernel_size=1,stride=1,padding=0,dilation=1,bias=False):
        super(SeparableConv2d,self).__init__()

        self.conv1 = nn.Conv2d(in_channels,in_channels,kernel_size,stride,padding,dilation,groups=in_channels,bias=bias)
        self.pointwise = nn.Conv2d(in_channels,out_channels,1,1,0,1,1,bias=bias)

    def forward(self,x):
        x = self.conv1(x)
        x = self.pointwise(x)
        return x

class Block(nn.Module):
    def __init__(self,in_filters,out_filters,reps,strides=1,activation=None):
        super(Block, self).__init__()

        if out_filters != in_filters or strides!=1:
            self.skip = nn.Conv2d(in_filters,out_filters,1,stride=strides, bias=False)
            self.skipbn = nn.BatchNorm2d(out_filters)
        else:
            self.skip=None

        act = nn.ReLU() if activation is None else activation
        rep=[]

        rep.append(act)
        rep.append(SeparableConv2d(in_filters,out_filters,3,stride=1,padding=1,bias=False))
        rep.append(nn.BatchNorm2d(out_filters))
        filters = out_filters

        for i in range(reps-1):
            rep.append(act)
            rep.append(SeparableConv2d(filters,filters,3,stride=1,padding=1,bias=False))
            rep.append(nn.BatchNorm2d(filters))

        if strides != 1:
            rep.append(nn.MaxPool2d(3,strides,1))
        self.rep = nn.Sequential(*rep)

    def forward(self,inp):
        x = self.rep(inp)

        if self.skip is not None:
            skip = self.skip(inp)
            skip = self.skipbn(skip)
        else:
            skip = inp

        x += skip
        return x

class AttrXception(nn.Module):
    def __init__(self, num_classes=1000):
        super(AttrXception, self).__init__()
        self.num_classes = num_classes

        self.conv1 = nn.Conv2d(3, 64, 3, 2, 1, bias=True)
        self.bn1 = nn.BatchNorm2d(64)
        self.mish = Mish()

        self.conv2 = nn.Conv2d(64, 128, 3, 1, 1, bias=True)
        self.bn2 = nn.BatchNorm2d(128)

        self.block1 = Block(128,256,2,2)
        self.block2 = Block(256,256,3,1)
        self.block3 = Block(256,256,3,1)
        self.block4 = Block(256,256,3,1)
        self.block5 = Block(256,256,3,1)
        self.block6 = Block(256,256,3,1)
        self.block7 = Block(256,384,2,2)

        self.conv3 = SeparableConv2d(384,512,3,stride=1,padding=0,bias=True)
        self.fc = nn.Linear(512, num_classes)

    def forward(self, input):
        x = self.conv1(input)
        x = self.bn1(x)
        x = self.mish(x)

        x = self.conv2(x)
        x = self.bn2(x)

        x = self.block1(x)
        x = self.block2(x)
        x = self.block3(x)
        x = self.block4(x)
        x = self.block5(x)
        x = self.block6(x)
        x = self.block7(x)

        x = self.mish(x)
        x = self.conv3(x)

        x = self.mish(x)
        x = F.adaptive_avg_pool2d(x, (1, 1))
        x = x.view(x.size(0), -1)
        result = self.fc(x)
        
        return torch.sigmoid(result)

class HourglassNet(nn.Module):
    def __init__(self, depth, channel):
        super(HourglassNet, self).__init__()
        self.depth = depth
        hg = []
        for _ in range(self.depth):
            hg.append([
                Block(channel,channel,3,1,activation=Mish()),
                Block(channel,channel,2,2,activation=Mish()),
                Block(channel,channel,3,1,activation=Mish())
            ])
        hg[0].append(Block(channel,channel,3,1,activation=Mish()))
        hg = [nn.ModuleList(h) for h in hg]
        self.hg = nn.ModuleList(hg)

    def _hour_glass_forward(self, n, x):
        up1 = self.hg[n-1][0](x)
        low1 = self.hg[n-1][1](up1)

        if n > 1:
            low2 = self._hour_glass_forward(n-1, low1)
        else:
            low2 = self.hg[n-1][3](low1)

        low3 = self.hg[n-1][2](low2)
        up2 = F.interpolate(low3, scale_factor=2)
        out = up1 + up2
        return out

    def forward(self, x):
        return self._hour_glass_forward(self.depth, x)

class XceptionHourglass(nn.Module):
    def __init__(self, num_classes):
        super(XceptionHourglass, self).__init__()
        self.num_classes = num_classes

        self.conv1 = nn.Conv2d(3, 128, 3, 2, 1, bias=True)
        self.bn1 = nn.BatchNorm2d(128)
        self.mish = Mish()

        self.conv2 = nn.Conv2d(128, 256, 3, 1, 1, bias=True)
        self.bn2 = nn.BatchNorm2d(256)

        self.block1 = HourglassNet(4, 256)
        self.bn3 = nn.BatchNorm2d(256)
        self.block2 = HourglassNet(4, 256)

        self.sigmoid = nn.Sigmoid()

        self.conv3 = nn.Conv2d(256, num_classes, 1, bias=True)

    def forward(self, input):
        x = self.conv1(input)
        x = self.bn1(x)
        x = self.mish(x)

        x = self.conv2(x)
        x = self.bn2(x)
        x = self.mish(x)

        out1 = self.block1(x)
        x = self.bn3(out1)
        x = self.mish(x)
        out2 = self.block2(x)

        r = self.sigmoid(out1 + out2)
        r = F.interpolate(r, scale_factor=2)
        
        return self.conv3(r)

class MaskDataset(object):
    def __init__(self, folder):
        self.imgids = [f.split(".")[0] for f in os.listdir(folder)]
        self.folder = folder

    def __getitem__(self, idx):
        imag = cv2.imread(self.folder+self.imgids[idx]+".jpg")
        imag = cv2.resize(imag, attr_image_size)
        return imag.transpose((2,0,1)).astype(np.float32)
        
    def __len__(self):
        return len(self.imgids)
    
import math
def _scale_image(img, long_size):
    if img.shape[0] < img.shape[1]:
        scale = img.shape[1] / long_size
        size = (long_size, math.floor(img.shape[0] / scale))
    else:
        scale = img.shape[0] / long_size
        size = (math.floor(img.shape[1] / scale), long_size)
    return cv2.resize(img, size, interpolation=cv2.INTER_NEAREST)

def get_ctgs_attrs(directory :str) :
    max_clz = train_df.ClassId.max()

    max_attr = 0
    for i in train_df.AttributesIds:
        for a in str(i).split(','):
            if a!='nan':
                a = int(a)
                if a > max_attr:
                    max_attr = a

    clz_attr = np.zeros((max_clz+1,max_attr+1))
    clz_attrid2idx = [[] for _ in range(max_clz+1)]

    for c,i in zip(train_df.ClassId,train_df.AttributesIds):
        for a in str(i).split(','):
            if a!='nan':
                a = int(a)
                clz_attr[c,a] = 1
                if not a in clz_attrid2idx[c]:
                    clz_attrid2idx[c].append(a)

    clz_attr_num = clz_attr.sum(axis=1).astype(np.int64)

    print("뿅")
    t = time.time()
    model = XceptionHourglass(max_clz+2)
    model.cuda()
    model.load_state_dict(torch.load(MODEL_FILE_DIR+"maskmodel_%d.model"%attr_image_size[0]))

    dataset = MaskDataset(directory)

    data_loader = torch.utils.data.DataLoader(
    dataset, batch_size=8, shuffle=False, num_workers=4)

    predict_imgeid = []
    predict_mask = []
    predict_rle = []
    predict_classid = []
    predict_attr = []

    imgid_cls_attrs = {}

    model.eval()
    prog = tqdm(data_loader, total=len(data_loader))
    num_pred = 0
    for X in prog:
        X = X.cuda()
        pred = model(X).detach().cpu().numpy()
        for i, mask in enumerate(pred):
            imgid = dataset.imgids[num_pred]
            num_pred += 1
            pred_id = mask.argmax(axis=0) - 1  # -1 is background.
            for clz in set(pred_id.reshape((-1,)).tolist()):
                if clz >= 0:
                    maskdata = (pred_id == clz).astype(np.uint8) * 255
                    predict_imgeid.append(imgid)
                    predict_mask.append(maskdata)
                    predict_rle.append("")
                    predict_classid.append(clz)
                    predict_attr.append([])
                    
                    if imgid not in imgid_cls_attrs.keys():
                        imgid_cls_attrs[imgid] = {}
                    imgid_cls_attrs[imgid][clz] = {"mask_size":np.sum(maskdata), "attributes":[]}
                    # test.append(imgid+" "+str(clz) + " "+ str(np.sum(maskdata)))

    prog, X, pred, dataset, data_loader = None, None, None, None, None
    torch.cuda.empty_cache()
    gc.collect()

    print(time.time()-t)

    for clzid in range(len(clz_attr_num)):
        if clz_attr_num[clzid] > 0 and os.path.isfile(MODEL_FILE_DIR+"attrmodel_%d-%d.model"%(attr_image_size[0],clzid)):
            # model = AttrXception(clz_attr_num[clzid])
            # model.cuda()
            # model.eval()
            # model.load_state_dict(torch.load(MODEL_FILE_DIR+"attrmodel_%d-%d.model"%(attr_image_size[0],clzid)))
            for i in range(len(predict_classid)):
                if predict_classid[i] == clzid:
                    imag = cv2.imread("C:/closed/test/imaterialist-fashion-2020-fgvc7/test2/"+predict_imgeid[i]+".jpg")
                    imag = _scale_image(imag, 1024)
                    mask = cv2.resize(predict_mask[i], (imag.shape[1],imag.shape[0]), interpolation=cv2.INTER_NEAREST)
                    where = np.where(mask!=0)
                    y1,y2,x1,x2 = 0,0,0,0
                    if len(where[0]) > 0 and len(where[1]) > 0:
                        y1,y2,x1,x2 = min(where[0]),max(where[0]),min(where[1]),max(where[1])
                        if y2>y1+80 and x2>x1+80 and np.sum(mask)/255 > 1000:
                            print("class id=",clzid)
                            plt.subplot(1,2,1)
                            plt.imshow(imag)
                            plt.subplot(1,2,2)
                            plt.imshow(mask)
                            plt.show()
                            # break

    uses_index = []
    for clzid in tqdm(range(len(clz_attr_num))):
        if clz_attr_num[clzid] > 0 and os.path.isfile(MODEL_FILE_DIR+"attrmodel_%d-%d.model"%(attr_image_size[0],clzid)):
            model = AttrXception(clz_attr_num[clzid])
            model.cuda()
            model.eval()
            model.load_state_dict(torch.load(MODEL_FILE_DIR+"attrmodel_%d-%d.model"%(attr_image_size[0],clzid)))
            for i in range(len(predict_classid)):
                if predict_classid[i] == clzid:
                    imag = cv2.imread("C:/closed/test/imaterialist-fashion-2020-fgvc7/test2/"+predict_imgeid[i]+".jpg")
                    imag = _scale_image(imag, 1024)
                    mask = cv2.resize(predict_mask[i], (imag.shape[1],imag.shape[0]), interpolation=cv2.INTER_NEAREST)
                    #imag[mask==0] = 255
                    where = np.where(mask!=0)
                    y1,y2,x1,x2 = 0,0,0,0
                    if len(where[0]) > 0 and len(where[1]) > 0:
                        y1,y2,x1,x2 = min(where[0]),max(where[0]),min(where[1]),max(where[1])
                        if y2>y1+80 and x2>x1+80 and np.sum(mask)/255 > 1000:
                            predict_rle[i] = mask_to_rle(mask)
                            X = cv2.resize(imag[y1:y2,x1:x2], attr_image_size).transpose((2,0,1))
                            attr_preds = model(torch.tensor([X], dtype=torch.float32).cuda())
                            attr_preds = attr_preds.detach().cpu().numpy()[0]
                            for ci in range(len(attr_preds)):
                                if attr_preds[ci] > 0.5:
                                    uses_index.append(i)
                                    predict_attr[i].append(clz_attrid2idx[predict_classid[i]][ci])

                                    imgid_cls_attrs[predict_imgeid[i]][predict_classid[i]]["attributes"].append(clz_attrid2idx[predict_classid[i]][ci])

    # class 분류 : 0~5, 6~8, 9~12 각각 하나로 취급, 하나의 사진에서 같은 분류(ex) upperbody 나올 시 마스킹 크기에 따라 참값으로 인식), 각각의 사진의 분류에 대하여 뽑아온 attr를 통합
    # 0~12 제외의 class는 각 사진별 빈도수 threshold 50%이상이면 있는 것으로 간주.(일단 임시로)
    # attr 통합 : supercategory = nickname 제외 같은 supercategory일 시 배제적으로 작동 => 빈도수로 결정, 아닐 시 추가하는 식으로(빈도수 50%이상).
    # attr - 배제적이지 않아도 되는 것 : nickname, silhouette, textile pattern

    [print(imgid_cls_attrs[x]) for x in imgid_cls_attrs.keys()]


    THRESHOLD = 0.4
    with open("C:/closed/test/imaterialist-fashion-2020-fgvc7/label_descriptions.json") as f:
        names_match = json.load(f)

    this_category = int(list(imgid_cls_attrs.keys())[0].split("_")[1]) #사용자 입력
    # dl, ul = [0, 0, 0, 0, 0, 0, 6, 6, 6, 9, 9, 9, 9], [5, 5, 5, 5, 5, 5, 8, 8, 8, 12, 12, 12, 12]
    pos = [
        [0, 1, 2, 3, 4], #0
        [0, 1, 2, 3, 4], #1
        [0, 1, 2, 3, 4], #2
        [0, 1, 2, 3, 4], #3
        [0, 1, 2, 3, 4], #4
        [5],          #5
        [6],             #6
        [7, 8],          #7
        [7, 8],          #8
        [3, 4, 9],       #9
        [10, 11],        #10
        [10, 11],        #11
        [12]             #12
        ]
    nan_class = [30, 34, 38, 41, 42, 44, 45]

    main_category_sc_attrs = {}
    sub_category = {} # cls : {frequency : value, supercategory : {attr : frequency}}
    result = {this_category : []}

    deleted = []
    flag = False
    for imgid in imgid_cls_attrs.keys():
        for ctg_pos in pos[this_category] :
            if ctg_pos in imgid_cls_attrs[imgid].keys():
                flag = True
    
    if not flag: deleted.append(imgid)

    for imgid in deleted:
        imgid_cls_attrs.pop(imgid)

    for imgid in imgid_cls_attrs.keys():
        this_main = {}
        for cls in imgid_cls_attrs[imgid].keys():
            if cls<=12 and cls in pos[this_category] :
                if not this_main:
                    this_main["class"] = cls
                    this_main["mask_size"] = imgid_cls_attrs[imgid][cls]["mask_size"]
                else:
                    if this_main["mask_size"] < imgid_cls_attrs[imgid][cls]["mask_size"]:
                        this_main["class"] = cls
                        this_main["mask_size"] = imgid_cls_attrs[imgid][cls]["mask_size"]
            
            elif cls>26:
                if cls not in sub_category.keys():
                    sub_category[cls] = {"frequency" : 1}

                    for attr in imgid_cls_attrs[imgid][cls]["attributes"]:
                        supercategory = names_match["attributes"][int(attr)]["supercategory"]
                        if supercategory not in sub_category[cls].keys():
                            sub_category[cls][supercategory] = {}
                        if attr not in sub_category[cls][supercategory].keys():
                            sub_category[cls][supercategory][attr] = 1
                        else:
                            sub_category[cls][supercategory][attr] += 1

                else :
                    sub_category[cls]["frequency"] += 1

                    for attr in imgid_cls_attrs[imgid][cls]["attributes"]:
                        supercategory = names_match["attributes"][int(attr)]["supercategory"]
                        if supercategory not in sub_category[cls].keys():
                            sub_category[cls][supercategory] = {}
                        if attr not in sub_category[cls][supercategory].keys():
                            sub_category[cls][supercategory][attr] = 1
                        else:
                            sub_category[cls][supercategory][attr] += 1

        for attr in imgid_cls_attrs[imgid][this_main["class"]]["attributes"]:
            supercategory = names_match["attributes"][int(attr)]["supercategory"]
            if supercategory not in main_category_sc_attrs.keys():
                main_category_sc_attrs[supercategory] = {}
            if attr not in main_category_sc_attrs[supercategory].keys():
                main_category_sc_attrs[supercategory][attr] = 1
            else :
                main_category_sc_attrs[supercategory][attr] += 1

    for sp in main_category_sc_attrs.keys():
        if sp == "nickname" or sp == "silhouette" or sp == "textile pattern":
            for id in main_category_sc_attrs[sp].keys():
                if main_category_sc_attrs[sp][id]/len(imgid_cls_attrs) >= THRESHOLD:
                    result[this_category].append(id)
        else :
            tmp = list(main_category_sc_attrs[sp].values())
            mx_id = list(main_category_sc_attrs[sp].keys())[tmp.index(max(tmp))]
            frequency = main_category_sc_attrs[sp][mx_id]
            if frequency/len(imgid_cls_attrs) >= THRESHOLD:
                result[this_category].append(mx_id)

    for cls in sub_category.keys():
        if sub_category[cls]["frequency"]/len(imgid_cls_attrs) < THRESHOLD:
            continue
        else :
            if cls not in result.keys():
                result[cls] = []
        
        for sp in sub_category[cls].keys():
            if sp != "frequency":
                if sp == "nickname" or sp == "silhouette" or sp == "textile pattern":
                    for id in sub_category[cls][sp].keys():
                        if sub_category[cls][sp][id]/len(imgid_cls_attrs) >= THRESHOLD:
                            result[cls].append(id)
                else :
                    tmp = list(sub_category[cls][sp].values())
                    mx_id = list(sub_category[cls][sp].keys())[tmp.index(max(tmp))]
                    frequency = sub_category[cls][sp][mx_id]
                    if frequency/len(imgid_cls_attrs) >= THRESHOLD:
                        result[cls].append(mx_id)

    for cls in result.keys():
        if not result[cls]:
            result[cls].append("nan")

    with open(f'C:/closed/test/imaterialist-fashion-2020-fgvc7/prod_info/{this_category}{imgid[:imgid.index("_")]}.json', 'w') as f:
        json.dump(result, f, indent=4)
    print(result)
