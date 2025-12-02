from django import template

register = template.Library()

@register.filter
def pagination_range(page_obj, margin=2):
    """
    فیلتر سفارشی برای ایجاد محدوده صفحات در pagination
    """
    current_page = page_obj.number
    total_pages = page_obj.paginator.num_pages
    
    # اگر تعداد صفحات کم باشد، همه را نمایش می‌دهیم
    if total_pages <= (margin * 2) + 3:
        return list(range(1, total_pages + 1))
    
    # محاسبه شروع و پایان
    start = max(1, current_page - margin)
    end = min(total_pages, current_page + margin)
    
    pages = []
    
    # همیشه صفحه اول
    pages.append(1)
    
    # اگر فاصله وجود دارد، ... نمایش داده می‌شود
    if start > 2:
        pages.append('...')
    
    # صفحات میانی
    for i in range(max(2, start), min(total_pages, end + 1)):
        pages.append(i)
    
    # اگر فاصله وجود دارد، ... نمایش داده می‌شود
    if end < total_pages - 1:
        pages.append('...')
    
    # همیشه صفحه آخر (اگر بیشتر از ۱ صفحه داریم)
    if total_pages > 1:
        pages.append(total_pages)
    
    return pages