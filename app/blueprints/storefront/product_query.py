from sqlalchemy import or_

from app.models.product import Product

PER_PAGE = 12

SORT_OPTIONS = {
    "mas_vendidos": (Product.is_featured.desc(), Product.created_at.desc()),
    "nuevos": (Product.created_at.desc(),),
    "precio_asc": (Product.price.asc(),),
    "precio_desc": (Product.price.desc(),),
}


def filtered_products(args, category=None, base_query=None):
    query = base_query if base_query is not None else Product.query.filter_by(is_active=True)

    if category is not None:
        query = query.filter(Product.category_id == category.id)

    search = args.get("q", "").strip()
    if search:
        like = f"%{search}%"
        query = query.filter(
            or_(Product.name.ilike(like), Product.short_description.ilike(like), Product.tags.ilike(like))
        )

    price_min = args.get("price_min", type=float)
    price_max = args.get("price_max", type=float)
    if price_min is not None:
        query = query.filter(Product.price >= price_min)
    if price_max is not None:
        query = query.filter(Product.price <= price_max)

    if args.get("in_stock"):
        query = query.filter(Product.stock > 0)
    if args.get("is_new"):
        query = query.filter(Product.is_new.is_(True))
    if args.get("on_sale"):
        query = query.filter(Product.compare_at_price.isnot(None))

    sort = args.get("sort", "mas_vendidos")
    query = query.order_by(*SORT_OPTIONS.get(sort, SORT_OPTIONS["mas_vendidos"]))

    page = args.get("page", 1, type=int)
    return query.paginate(page=page, per_page=PER_PAGE, error_out=False)
