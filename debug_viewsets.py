#!/usr/bin/env python
import os
import sys
import django

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

try:
    print("=== Debugging ViewSet Registration ===")
    
    # Try importing views module
    print("1. Importing views module...")
    from backend.production import views
    print("Views module imported successfully")
    
    # Check if IsIstasyonuViewSet exists
    print("\n2. Checking IsIstasyonuViewSet...")
    if hasattr(views, 'IsIstasyonuViewSet'):
        print("IsIstasyonuViewSet found")
        print(f"   Class: {views.IsIstasyonuViewSet}")
        print(f"   Queryset: {views.IsIstasyonuViewSet.queryset}")
    else:
        print("IsIstasyonuViewSet NOT found")
    
    # Try importing urls module
    print("\n3. Importing urls module...")
    from backend.production import urls
    print("URLs module imported successfully")
    
    # Check router registry
    print("\n4. Checking router registry...")
    print(f"   Router registry length: {len(urls.router.registry)}")
    
    for i, (prefix, viewset, basename) in enumerate(urls.router.registry):
        print(f"   {i+1}. {prefix} -> {viewset.__name__} (basename: {basename})")
    
    # Try generating URLs
    print("\n5. Generating URLs...")
    router_urls = urls.router.get_urls()
    print(f"   Generated {len(router_urls)} URLs")
    
    for url in router_urls[:10]:  # Show first 10
        print(f"   - {url.pattern}")
        
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()