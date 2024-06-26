package com.team4.shoppingmall.seller_prod_stock;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import lombok.ToString;

@ToString
@Getter@Setter
@NoArgsConstructor
@AllArgsConstructor
public class Seller_Prod_StockDTO {
	Integer stock_id;
	Integer s_p_stock;
	Integer s_p_sell;
	Integer prod_id;
	Integer opt_id1;
	Integer opt_id2;
	Integer opt_id3;
	Integer opt_id4;
	Integer opt_id5;
	Integer review_id;
}