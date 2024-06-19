<%@ page language="java" contentType="text/html; charset=UTF-8"
	pageEncoding="UTF-8"%>
<%@taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core"%>
<c:set var="path" value="${pageContext.servletContext.contextPath}" />
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>상품 상세 페이지</title>
<%-- css --%>
<link rel="stylesheet" href="${path}/resources/css/product_detail.css">
<%-- 헤더,푸터 css --%>
<link rel="stylesheet" href="${path}/resources/css/header_footer.css">
<%-- jquery 연결 --%>
<script src="${path}/resources/js/jquery-3.7.1.min.js"></script>
<script
	src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
<script>
	$(function() {
		//배송 안내 정보 토글
		$('.toggle-button').click(function() {
			$('.toggle-content').slideToggle();
			$('.arrow').toggleClass('open');
		});

		//상품 상세 정보, 리뷰 버튼 조작  (수정필요! 리뷰버튼 클릭하고 상품정보버튼 클릭하면 상품정보내용이 안나타남)
		$('.detailbtn_wrap button').click(function() {
			// 버튼에 active 클래스 적용
			$('.detailbtn_wrap button').removeClass('this');
			$(this).addClass('this');

			// 관련된 컨텐츠 표시
			var tabId = $(this).data('tab');
			$('.container-detail, .container-review').removeClass('active');
			$('#' + tabId).addClass('active');
		});

		//상품 문의 팝업창 열고 닫기 
		$('.qnaBtn').on('click', function() {
			$('#myModal').show();
		});

		$('.close').on('click', function() {
			$('#myModal').hide();
		});

		$(window).on('click', function(event) {
			if ($(event.target).is('#myModal')) {
				$('#myModal').hide();
			}
		});
		
	});

</script>

</head>
<body>
	<%@ include file="../common/header.jsp" %>
	
	<%-- 브랜치테스트 2 --%>
	
	<%-- 팝업 배경 --%>
	<div class="popup-background" id="popupBackground">
	    <%-- 팝업 컨테이너 --%>
	    <div class="popup-container">
	        <%-- 팝업 아이콘 --%>
	        <div class="popup-icon">!</div>
	        <%-- 팝업 메시지 --%>
	        <p>계속 쇼핑하시겠습니까?</p>
	        <!-- 팝업 버튼 -->
	        <button class="popup-button no-button">네</button>
	        <button class="popup-button yes-button">장바구니로 이동</button>
	    </div>
	</div>
	
	<div id="myModal" class="modal">
		<div class="modal-content">
			<span class="close">&times;</span>
			<div class="modal-header">
				<h1>상품문의</h1>
			</div>
			<div class="modal-body">
				<label for="qnaTitle">문의 제목: </label>
				<input type="text" name="qnaTitle" placeholder="문의 제목" />
				<p>상품과 관련 없는 내용, 비방, 광고, 불건전한 내용의 글은 사전 동의 없이 삭제될 수 있습니다.</p>
				<textarea
					placeholder="문의 내용을 입력해주세요. 특수문자 &#87, &#47, &#60, &#62 는 사용할 수 없습니다.">
				</textarea>
				<br> 
				<input type="text" placeholder="이름" />
			</div>
			<div class="modal-footer">
				<button type="button">등록</button>
			</div>
		</div>
	</div>
	
	<div class="container">
		<div class="inner">
			<p>home > 의류 > 바람</p>
			<div class="product-detail_wrap">
				<div class="product-image">
					<img src="${path}/resources/images/product1.png" alt="상품">
				</div>
				<div class="product-details">
					<p class="free">무료배송</p>
					<h1>NIKE</h1>
					<h2>나이키 드라이핏 스우시 반팔티</h2>
					<div class="price_wrap">
						<p class="productPrice">
							<del>100,000원</del>
						</p>
						<p>
							<span class="discount">60%</span> 
							<span class="discountPrice">40,000원</span>
						</p>
					</div>
					<p class="rate">
						★ 4.5 <span><a href="#void">리뷰 8건</a></span>
					</p>
					<form id="prodOptionFrom">
						<div class="choose_wrap">
							<p>선택</p>
							<div class="select_choose">
								<%-- 카테고리 : 의류 > 상의 --%>
								<select id="product-size" name="product-size">
									<option value="0" selected="selected">선택</option>
									<option value="L" selected>상의 (L)</option>
									<option value="M">상의 (M)</option>
									<option value="S">상의 (S)</option>
								</select> 
								<select id="product-color" name="product-color">
									<option value="0" selected="selected">선택</option>
									<option value="RED" selected>색상 (BLACK)</option>
									<option value="RED">색상 (RED)</option>
									<option value="RED">색상 (GREEN)</option>
								</select>
							</div>
						</div>
						<div class="quantity-price">
							<div class="quantity_wrap">
								<p>수량 선택 :</p>
								<input type="number" id="quantity" class="quantity"
									name="quantity" value="1" min="1">
							</div>
							<p class="total">40,000원</p>
						</div>
						<%-- 단가 --%>
						<input type="hidden" name="discountPrice" value="40000">
					</form>
					<div class="button-group">
						<button id="cartButton" type="button" class="white_button" onclick="prodOption()">장바구니</button>
						<button type="button" class="button">바로 구매</button>
					</div>
					<button type="button" class="noRent_btn">대여불가상품</button>
				</div>
			</div>
			<%-- 상품정보, 리뷰 버튼 --%>
			<div id="detailbtn_wrap" class="detailbtn_wrap">
				<button type="button" class="this" data-tab="container-detail">상품
					정보</button>
				<button type="button" data-tab="container-review">리뷰</button>
			</div>
			<%-- 상세정보 --%>
			<div class="container-detail active">
				<div>
					<h1 style="text-align: center;">상품 정보 이미지 등록할 부분</h1>
				</div>
			</div>
			<%-- 리뷰 목록 --%>
			<div id="container-review" class="container-review inner">
				<h1>상품 리뷰</h1>
				<ul class="review_order">
					<li><a href="javascript:#void">최근 등록 순</a></li>
					<li><a href="javascript:#void">평점 높은 순</a></li>
					<li><a href="javascript:#void">평점 낮은 순</a></li>
				</ul>
				<p class="no-review hidden">작성된 리뷰가 없습니다.</p>
				<div class="review-list">
					<div class="review-scroll">
						<div class="review">
							<div class="left">
								<img src="path/to/image.jpg" alt="review image">
							</div>
							<div class="right">
								<div class="rating">
									<span>★★★★★</span>
								</div>
								<h3>색상: 검정색 / 사이즈: L</h3>
								<p>생각보다 엄청 밝아요!</p>
								<p class="date">2024.05.18</p>
							</div>
						</div>
						<div class="review">
							<div class="left">
								<img src="path/to/image.jpg" alt="review image">
							</div>
							<div class="right">
								<div class="rating">
									<span>★★★★★</span>
								</div>
								<h3>색상: 검정색 / 사이즈: L</h3>
								<p>생각보다 엄청 밝아요!</p>
								<p class="date">2024.05.18</p>
							</div>
						</div>
						<div class="review">
							<div class="left">
								<img src="path/to/image.jpg" alt="review image">
							</div>
							<div class="right">
								<div class="rating">
									<span>★★★★★</span>
								</div>
								<h3>색상: 검정색 / 사이즈: L</h3>
								<p>생각보다 엄청 밝아요!</p>
								<p class="date">2024.05.18</p>
							</div>
						</div>
						<div class="review">
							<div class="left">
								<img src="path/to/image.jpg" alt="review image">
							</div>
							<div class="right">
								<div class="rating">
									<span>★★★★★</span>
								</div>
								<h3>색상: 검정색 / 사이즈: L</h3>
								<p>생각보다 엄청 밝아요!</p>
								<p class="date">2024.05.18</p>
							</div>
						</div>
						<div class="review">
							<div class="left">
								<img src="path/to/image.jpg" alt="review image">
							</div>
							<div class="right">
								<div class="rating">
									<span>★★★★★</span>
								</div>
								<h3>색상: 검정색 / 사이즈: L</h3>
								<p>생각보다 엄청 밝아요!</p>
								<p class="date">2024.05.18</p>
							</div>
						</div>
						<div class="review">
							<div class="left">
								<img src="path/to/image.jpg" alt="review image">
							</div>
							<div class="right">
								<div class="rating">
									<span>★★★★★</span>
								</div>
								<h3>색상: 검정색 / 사이즈: L</h3>
								<p>생각보다 엄청 밝아요!</p>
								<p class="date">2024.05.18</p>
							</div>
						</div>
						<div class="review">
							<div class="left">
								<img src="path/to/image.jpg" alt="review image">
							</div>
							<div class="right">
								<div class="rating">
									<span>★★★★★</span>
								</div>
								<h3>색상: 검정색 / 사이즈: L</h3>
								<p>생각보다 엄청 밝아요!</p>
								<p class="date">2024.05.18</p>
							</div>
						</div>
						<div class="review">
							<div class="left">
								<img src="path/to/image.jpg" alt="review image">
							</div>
							<div class="right">
								<div class="rating">
									<span>★★★★★</span>
								</div>
								<h3>색상: 검정색 / 사이즈: L</h3>
								<p>생각보다 엄청 밝아요!</p>
								<p class="date">2024.05.18</p>
							</div>
						</div>
					</div>
				</div>
				<button class="button-write">리뷰 작성하기</button>
			</div>

			<div class="qa-section inner">
				<h2>상품 Q&A</h2>
				<div class="qa-section_txt">
					<p>등록된 상품 Q&A가 없습니다.</p>
					
					<%-- 상품 문의 있을 경우 테이블 생성 --%>
					
					<button class="button-write qnaBtn">상품 문의하기</button>
				</div>
			</div>

			<%-- 배송 정보 안내 --%>
			<div class="toggle-button inner">
				<h2>배송/교환/반품 안내</h2>
				<span class="arrow">▼</span>
			</div>
			<div class="toggle-content inner">
				<h3>배송안내</h3>
				<table>
					<tr>
						<td>일반 택배</td>
						<td>
							<p>전제품 국내산지에서 직접 배송하는 상품입니다.</p>
							<p>일반 택배: 전제품 국내산지에서 3일 이내 배송 (토,일,공휴일 제외)</p>
						</td>
					</tr>
					<tr>
						<td>교환/반품비용</td>
						<td>교환/반품 배송비: 2,500원 (CJ대한통운 교환/반품 수거 비용)</td>
					</tr>
					<tr>
						<td>교환/반품</td>
						<td>
							<p>1. 마이페이지에서 교환 신청 (단순 변심인 경우, 교환은 원하는 옵션 선택 후 교환신청)</p>
							<p>2. 교환 요청한 제품 회수하기 위해 반송비가 부과되는 경우 결제 완료 교환 선수</p>
							<p>3. 1~3일 내 반품 제품 수거 (택배 선택 검토 필요)</p>
							<p>4. 회수 제품 확인 후 상품 배송 (반품/교환 신청된 제품 외 교환/반품 배송)</p>
						</td>
					</tr>
					<tr>
						<td>안내사항</td>
						<td>
							<p>교환 기간: 교환은 제품을 받은 후 7일 내 가능합니다.</p>
							<p>반품 기간: 반품은 제품을 받은 후 7일 내 가능합니다.</p>
							<p>단순 변심일 경우 최초 배송한 상품의 상태와 다를 시 (세탁 또는 착용 후 외형 변형) 교환 및 반품이
								불가합니다.</p>
							<p>교환/반품 배송비: 2,500원 (CJ대한통운 교환/반품 수거 비용)</p>
						</td>
					</tr>
					<tr>
						<td>고객 A/S 안내</td>
						<td>이 상품은 입점사상품으로, 입점사의 A/S 정책에 따라 서비스가 제공됩니다. 상세한 문의사항은
							상품정보고객센터 및 A/S센터가 갖춘 정보를 확인해주세요.
						</td>
					</tr>
				</table>
			</div>
		</div>
	</div>
	<%@ include file="../common/footer.jsp" %>
	<script>
        $(document).ready(function() {
            // 원래 가격 (숫자만 추출)
            var originalPrice = parseInt($('.productPrice del').text().replace(/[^0-9]/g, ''));

            // 할인율 (숫자만 추출)
            var discountRate = parseInt($('.discount').text().replace(/[^0-9]/g, ''));

            // 할인된 가격 계산 
            var discountedPrice = originalPrice * (1 - discountRate / 100);

            // 할인된 가격을 3자리 콤마 형식으로 업데이트 (예: 10,000원)
            $('.discountPrice').text(discountedPrice.toLocaleString() + '원');

            // 초기 총 가격 설정
            $('.total').text(discountedPrice.toLocaleString() + '원');

            var previousValue = parseInt($('.quantity').val());

            // 수량 입력 필드가 변경될 때마다 실행
            $('.quantity').on('input', function() {
                var currentValue = parseInt($(this).val()); // 수량

                if (currentValue < previousValue) {
                    console.log('수량이 감소 : ' + currentValue);
                } else {
                    console.log('수량이 증가: ' + currentValue);
                }

                // previousValue를 현재 값으로 업데이트
                previousValue = currentValue;

                // 할인된 가격과 총 가격 업데이트 로직
                var totalPrice = discountedPrice * currentValue;
                $('.total').text(totalPrice.toLocaleString() + '원');
            });
    		
    		//장바구니 버튼 선택 시 나타나는 팝업창 
    		//$('#cartButton').on('click', function() {
    		//	$('.popup-background').show();
    		//});
    		//계속 쇼핑 선택시
    		//$('.no-button').on('click', function() {
    		//	$('.popup-background').hide();
    		//});
    		//계속 쇼핑 선택시
    		//$('.yes-button').on('click', function() {
    		//	location.href= "${path}/cart/cart"; //장바구니 페이지 이동(수정중)
    		//});
    		
        });
    	
		//버튼 클릭 -> 컨트롤러에 상품 옵션 값 저장
		function prodOption(){
		        
	       //컨트롤러에 상품 옵션 값 보내기
		   var param = $("#prodOptionFrom").serialize();
		   //location.href : Get요청
		   location.href= "${path}/customer/productOption?" + param;
		}
    </script>
</body>
</html>