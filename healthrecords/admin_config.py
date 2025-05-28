from django.contrib import admin

def configure_admin_site():
    admin.site.site_header = "Health Records Administration"
    admin.site.site_title = "Health Records Admin Portal"
    admin.site.index_title = "Welcome to Health Records Admin Portal" 