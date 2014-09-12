def fetch(sql):
  sqls={}
  # get product count per category
  sqls['sql_productPERcategory'] = """select category, count(distinct(product_id) from Product group by category order by category;"""

# product_id order by category
  sqls['sql_productORDERBYcategory'] = """select distinct product_id from Product order by category;"""

# reviews from reviewer who did multiple reviews
  sqls['sql_reviews'] = """select reviewer_id from (select reviewer_id, reviewer_name, count(Review.review_id) as c from Reviewer join Review where Review.review_id = Reviewer.review_id group by reviewer_id order by c desc) as review_counts where review_counts.c > 1;"""

#
  sqls['sql_ratings'] = """select reviewer_id, product_id, rating
        from Reviewer join Review
        where Review.review_id = Reviewer.review_id """


  return sqls[sql]
