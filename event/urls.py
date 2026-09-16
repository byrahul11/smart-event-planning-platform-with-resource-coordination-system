from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('chatbot/', views.chatbot_view, name='chatbot'),

    # ---- User Panel (Milestone 3) ----
    path('my-dashboard/', views.user_dashboard_view, name='user_dashboard'),

    # ---- Events ----
    path('events/', views.event_list_view, name='event_list'),
    path('events/create/', views.create_event_view, name='create_event'),
    path('events/completed/', views.complete_event_list_view, name='complete_event_list'),
    path('events/<int:pk>/', views.event_details_view, name='event_details'),
    path('events/<int:pk>/edit/', views.edit_event_view, name='edit_event'),
    path('events/<int:pk>/delete/', views.delete_event_view, name='delete_event'),

    # ---- Categories ----
    path('categories/', views.category_list_view, name='category_list'),
    path('categories/create/', views.create_category_view, name='create_category'),
    path('categories/<int:pk>/', views.category_details_view, name='category_details'),
    path('categories/<int:pk>/edit/', views.edit_category_view, name='edit_category'),
    path('categories/<int:pk>/delete/', views.delete_category_view, name='delete_category'),

    # ---- Profile & Theme Settings (Milestone 3) ----
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('settings/theme/', views.theme_settings_view, name='theme_settings'),
    path('settings/theme/reset/', views.reset_theme_view, name='reset_theme'),
    path('settings/dark-mode/toggle/', views.toggle_dark_mode_view, name='toggle_dark_mode'),

    # ---- Event Members (Milestone 3) ----
    path('members/', views.event_member_list_view, name='event_member_list'),
    path('members/add/', views.add_event_member_view, name='add_event_member'),
    path('members/<int:pk>/delete/', views.delete_event_member_view, name='delete_event_member'),

    # ---- Registration / Tickets (Milestone 3) ----
    path('events/<int:pk>/register/', views.register_for_event_view, name='register_for_event'),
    path('ticket/<str:ticket_id>/', views.view_ticket_view, name='view_ticket'),
    path('ticket/<str:ticket_id>/pdf/', views.download_ticket_pdf_view, name='download_ticket_pdf'),
    path('my-tickets/', views.my_tickets_view, name='my_tickets'),
    path('registrations/', views.admin_registration_list_view, name='admin_registration_list'),

    # ---- Wishlist (Milestone 3) ----
    path('events/<int:pk>/wishlist/', views.toggle_wishlist_view, name='toggle_wishlist'),
    path('wishlist/', views.admin_wishlist_list_view, name='admin_wishlist_list'),
    path('wishlist/add/', views.add_wishlist_user_view, name='add_wishlist_user'),

    # ---- Attendance / QR Scan (Milestone 3) ----
    path('attendance/scan/', views.scan_qr_view, name='scan_qr'),

    # ---- Finance / Budget (Milestone 3) ----
    path('finance/budgets/', views.budget_list_view, name='budget_list'),
    path('finance/budgets/create/', views.create_budget_view, name='create_budget'),
    path('finance/budgets/<int:pk>/edit/', views.edit_budget_view, name='edit_budget'),
    path('finance/budgets/<int:pk>/delete/', views.delete_budget_view, name='delete_budget'),
    path('finance/analysis/', views.finance_analysis_view, name='finance_analysis'),

    # ---- Notifications (Milestone 3) ----
    path('notifications/', views.notifications_list_view, name='notification_list'),
    path('notifications/mark-read/', views.mark_notifications_read_view, name='mark_notifications_read'),

        # ---- Admin Inbox (Milestone 4) ----
    path('contact-admin/', views.contact_admin_view, name='contact_admin'),
    path('inbox/', views.admin_inbox_list_view, name='admin_inbox'),
    path('inbox/<int:user_id>/', views.admin_thread_view, name='admin_thread'),
]
