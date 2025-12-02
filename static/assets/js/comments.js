/**
 * سیستم مدیریت نظرات - نسخه نهایی
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ سیستم نظرات بارگذاری شد');
    
    // مقداردهی اولیه سیستم نظرات
    window.commentSystem = new CommentSystem();
});

class CommentSystem {
    constructor() {
        this.csrfToken = this.getCSRFToken();
        this.currentReplyForm = null;
        this.init();
    }
    
    init() {
        console.log('✅ سیستم نظرات راه‌اندازی شد');
        
        // راه‌اندازی دکمه‌های پاسخ
        this.setupReplyButtons();
        
        // راه‌اندازی فرم‌های پاسخ
        this.setupReplyForms();
        
        // راه‌اندازی فرم نظر اصلی
        this.setupMainCommentForm();
        
        // راه‌اندازی دکمه‌های انصراف
        this.setupCancelButtons();
    }
    
    // دریافت CSRF Token
    getCSRFToken() {
        const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
        return csrfInput ? csrfInput.value : '';
    }
    
    // راه‌اندازی دکمه‌های پاسخ
    setupReplyButtons() {
        console.log('در حال راه‌اندازی دکمه‌های پاسخ...');
        
        // استفاده از event delegation
        document.addEventListener('click', (e) => {
            // اگر روی دکمه پاسخ کلیک شد
            if (e.target.closest('.btn-reply')) {
                e.preventDefault();
                e.stopPropagation();
                
                const button = e.target.closest('.btn-reply');
                const commentId = button.getAttribute('data-comment-id');
                console.log('کلیک روی دکمه پاسخ برای نظر:', commentId);
                
                // نمایش فرم پاسخ
                this.toggleReplyForm(commentId);
            }
        });
    }
    
    // نمایش یا مخفی کردن فرم پاسخ
    toggleReplyForm(commentId) {
        console.log('نمایش فرم پاسخ برای:', commentId);
        
        const formContainer = document.getElementById(`reply-form-container-${commentId}`);
        if (!formContainer) {
            console.error('فرم پاسخ پیدا نشد برای ID:', commentId);
            return;
        }
        
        // مخفی کردن همه فرم‌های پاسخ دیگر
        document.querySelectorAll('.reply-form-container').forEach(form => {
            if (form.id !== `reply-form-container-${commentId}`) {
                form.style.display = 'none';
            }
        });
        
        // نمایش/مخفی کردن فرم جاری
        if (formContainer.style.display === 'none' || formContainer.style.display === '') {
            formContainer.style.display = 'block';
            this.currentReplyForm = commentId;
            
            // اسکرول به فرم
            setTimeout(() => {
                formContainer.scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'nearest' 
                });
                
                // فوکوس روی textarea
                const textarea = formContainer.querySelector('textarea');
                if (textarea) {
                    textarea.focus();
                }
            }, 100);
        } else {
            formContainer.style.display = 'none';
            this.currentReplyForm = null;
        }
    }
    
    // راه‌اندازی فرم‌های پاسخ
    setupReplyForms() {
        console.log('در حال راه‌اندازی فرم‌های پاسخ...');
        
        // استفاده از event delegation برای فرم‌ها
        document.addEventListener('submit', (e) => {
            if (e.target.closest('.reply-form')) {
                e.preventDefault();
                const form = e.target.closest('.reply-form');
                const commentId = form.getAttribute('data-comment-id');
                
                this.submitReplyForm(form, commentId);
            }
        });
    }
    
    // ارسال فرم پاسخ
    async submitReplyForm(form, commentId) {
        const formData = new FormData(form);
        const submitButton = form.querySelector('button[type="submit"]');
        const originalButtonText = submitButton.textContent;
        
        // اعتبارسنجی
        const body = formData.get('body');
        if (!body.trim()) {
            this.showAlert('لطفا متن پاسخ را وارد کنید', 'error');
            return;
        }
        
        try {
            // نمایش حالت لودینگ
            submitButton.disabled = true;
            submitButton.innerHTML = '<span class="spinner-border spinner-border-sm"></span> در حال ارسال...';
            
            // ارسال درخواست
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': this.csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showAlert('پاسخ شما با موفقیت ثبت شد', 'success');
                form.reset();
                
                // مخفی کردن فرم پاسخ
                this.hideReplyForm(commentId);
                
                // رفرش صفحه بعد از 1.5 ثانیه
                setTimeout(() => {
                    window.location.reload();
                }, 1500);
            } else {
                this.showAlert(data.error || 'خطا در ارسال پاسخ', 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            this.showAlert('خطا در ارتباط با سرور', 'error');
        } finally {
            // بازگرداندن دکمه به حالت عادی
            submitButton.disabled = false;
            submitButton.textContent = originalButtonText;
        }
    }
    
    // مخفی کردن فرم پاسخ
    hideReplyForm(commentId) {
        const formContainer = document.getElementById(`reply-form-container-${commentId}`);
        if (formContainer) {
            formContainer.style.display = 'none';
        }
        this.currentReplyForm = null;
    }
    
    // راه‌اندازی فرم نظر اصلی
    setupMainCommentForm() {
        const form = document.getElementById('new-comment-form');
        
        if (!form) {
            console.log('فرم نظر اصلی پیدا نشد');
            return;
        }
        
        console.log('در حال راه‌اندازی فرم نظر اصلی...');
        
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(form);
            const submitButton = form.querySelector('button[type="submit"]');
            const originalButtonText = submitButton.textContent;
            
            // اعتبارسنجی
            const body = formData.get('body');
            if (!body.trim()) {
                this.showAlert('لطفا متن نظر را وارد کنید', 'error');
                return;
            }
            
            try {
                // نمایش حالت لودینگ
                submitButton.disabled = true;
                submitButton.innerHTML = '<span class="spinner-border spinner-border-sm"></span> در حال ارسال...';
                
                // ارسال درخواست
                const response = await fetch(form.action, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': this.csrfToken,
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });
                
                const data = await response.json();
                
                if (data.success) {
                    this.showAlert('نظر شما با موفقیت ثبت شد', 'success');
                    form.reset();
                    
                    // رفرش صفحه بعد از 1.5 ثانیه
                    setTimeout(() => {
                        window.location.reload();
                    }, 1500);
                } else {
                    this.showAlert(data.error || 'خطا در ارسال نظر', 'error');
                }
            } catch (error) {
                console.error('Error:', error);
                this.showAlert('خطا در ارتباط با سرور', 'error');
            } finally {
                // بازگرداندن دکمه به حالت عادی
                submitButton.disabled = false;
                submitButton.textContent = originalButtonText;
            }
        });
    }
    
    // راه‌اندازی دکمه‌های انصراف
    setupCancelButtons() {
        document.addEventListener('click', (e) => {
            if (e.target.closest('.btn-cancel-reply')) {
                e.preventDefault();
                const button = e.target.closest('.btn-cancel-reply');
                const commentId = button.getAttribute('data-comment-id');
                
                this.hideReplyForm(commentId);
            }
        });
    }
    
    // نمایش پیام
    showAlert(message, type) {
        // حذف آلرت‌های قبلی
        const existingAlerts = document.querySelectorAll('.custom-alert');
        existingAlerts.forEach(alert => {
            alert.remove();
        });
        
        // ایجاد آلرت جدید
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type === 'success' ? 'success' : 'danger'} alert-dismissible fade show`;
        alertDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        `;
        
        alertDiv.innerHTML = `
            <strong>${type === 'success' ? '✅ موفقیت!' : '❌ خطا!'}</strong>
            <span>${message}</span>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alertDiv);
        
        // حذف خودکار بعد از 5 ثانیه
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
}