from django.urls import path

from .contactus import ContactUsView
from .products import ProductView, ProductSearchView, GetAllProductsView, UpdateProductView, GetAllCategoriesView
from .orgs import MapJsonView, RegisterView, OrgView, UpdateOrgLogoView, GetAllOrgsView, checkOrgPhoneNumber, \
    checkOrgName, checkOrgAddress, checkOrgGST, UpdateOrgView, UpdateOrgStateView, OrgByIdView
from .users import CheckUserView, SetPasswordView, LoginView, GetUserView, CreateUserAPIToken, UpdateUserAPIToken, \
    GetUserAPIToken, RefreshTokenView, RegisterUserView, GetAllUsersView, UpdateUserView, PopulateUserRolesView, \
    ResetPasswordView
from .verify_user import SendVerificationCodeView, CheckVerificationCodeView, ReSendVerificationCodeView
from .applications import ProductApplicationView, ProductItemsView, UploadFileView, ApplicationItemView, \
    ApplicationFeedbackView, UpdateApplicationStatusView, ApplicationsView, ApplicationDetailsView, \
    ApplicationUniqueItemView, ApplicationItemsView, UpdateApplicationItemView, SearchApplicationView, \
    SearchApplicationItemView, IndiannessPercentageView, ReviewApplicationView, \
    CheckForApplicationView, SearchApplicationView_V2, GetApplicationStatsView, AssignApplicationView, \
    ResubmitApplicationView, UpdateApplicationView

urlpatterns = [
    path('get_map_json/', MapJsonView.as_view(), name='get_map_json'),
    path('check-user/', CheckUserView.as_view(), name='check-user'),
    path('login/', LoginView.as_view(), name='login'),
    path('send-verification-code/', SendVerificationCodeView.as_view(), name='send-verification-code'),
    path('check-verification-code/', CheckVerificationCodeView.as_view(), name='check-verification-code'),
    path('set-password/', SetPasswordView.as_view(), name='set-password'),
    path('register/', RegisterView.as_view(), name='onboard'),
    path('product-apply/', ProductApplicationView.as_view(), name='product-apply'),
    path('products/<application_id>', ProductItemsView.as_view(), name='products-register'),
    path('products/<application_id>/', ProductItemsView.as_view(), name='products-register'),
    path('upload/', UploadFileView.as_view(), name='upload-file'),
    path('add-product/', ProductView.as_view(), name='add-product'),
    path('product/<external_application_id>/<sequence_id>/', ApplicationItemView.as_view(), name='product-details'),
    path('org-details/', OrgView.as_view(), name='get-org-details'),
    path('search-product/', ProductSearchView.as_view(), name='search_product'),
    path('submit-feedback/', ApplicationFeedbackView.as_view(), name='submit_feedback'),
    path('application/<external_application_id>/update-status/',
         UpdateApplicationStatusView.as_view(),
         name='update_application_status'),
    path('get-user/', GetUserView.as_view(), name='get-user'),
    path('applications/', ApplicationsView.as_view(), name='get-applications'),
    path('application/<application_id>/details/', ApplicationDetailsView.as_view(), name='get-application-details'),
    path('product/<external_application_id>/<sequence_id>/<item_key>/', ApplicationUniqueItemView.as_view(),
         name='unique-product-details'),
    path('generate-api-token/', CreateUserAPIToken.as_view(), name='generate-api-token'),
    path('update-api-token/', UpdateUserAPIToken.as_view(), name='update-api-token'),
    path('application/<application_id>/items/', ApplicationItemsView.as_view(), name='application-items'),
    path('get-api-token/', GetUserAPIToken.as_view(), name='get-api-token'),
    path('application-item/<item_id>/update/', UpdateApplicationItemView.as_view(), name='update-application-items'),
    path('update-org-logo/<org_id>/', UpdateOrgLogoView.as_view(), name='update-org-logo'),
    path("search-application/<org_id>/", SearchApplicationView.as_view(), name="search-application"),
    path("search-application-v2/", SearchApplicationView_V2.as_view(), name="search-application-v2"),
    path("search-application-item/<application_id>/", SearchApplicationItemView.as_view(),
         name="search-application-item"),
    path("calculate-indianness/", IndiannessPercentageView.as_view(), name="calculate-product-indianness"),
    path('refresh-token/', RefreshTokenView.as_view(), name='token_refresh'),
    path('application-review/', ReviewApplicationView.as_view(), name='review_application'),
    path('resubmit-application/<application_id>/', ResubmitApplicationView.as_view(), name='resubmit_application'),
    path('check-for-application/<product_id>/', CheckForApplicationView.as_view(), name='check_for_application'),
    path('get-all-orgs/', GetAllOrgsView.as_view(), name='get-all-orgs'),
    path('get-all-products/', GetAllProductsView.as_view(), name='get-all-products'),
    path('update-product/<product_id>/', UpdateProductView.as_view(), name='update-product'),
    path('register-user/', RegisterUserView.as_view(), name='register-user'),
    path('get-all-users/', GetAllUsersView.as_view(), name='get-all-users'),
    path('update-user/<user_id>/', UpdateUserView.as_view(), name='update-user'),
    path('get-applications-stats/', GetApplicationStatsView.as_view(), name='get-applications-stats'),
    path('assign-application/<application_id>/', AssignApplicationView.as_view(), name='assign_application'),
    path('get-all-product-categories/', GetAllCategoriesView.as_view(), name='get-all-product-categories'),
    path('populate-user-roles/', PopulateUserRolesView.as_view(), name='populate-user-roles'),
    path('check-org-phone-number/', checkOrgPhoneNumber.as_view(), name='check-org-phone-number'),
    path('check-org-name/', checkOrgName.as_view(), name='check-org-name'),
    path('check-org-address/', checkOrgAddress.as_view(), name='check-org-address'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('check-org-gst/', checkOrgGST.as_view(), name='check-org-GST'),
    path('update-org/<org_id>/', UpdateOrgView.as_view(), name='update-org'),
    path('update-org-state/<org_id>/', UpdateOrgStateView.as_view(), name='update-org-state'),
    path('resend-verification-code/', ReSendVerificationCodeView.as_view(), name='resend-verification-code'),
    path('contact-us/', ContactUsView.as_view(), name='contact_us'),
    path('update-application/<application_id>/', UpdateApplicationView.as_view(),
         name='update-application'),
    path('resend-verification-code/', ReSendVerificationCodeView.as_view(), name='resend-verification-code'),
    path('get-org-details-by-id/<org_id>/', OrgByIdView.as_view(), name='get-org-details-by-id'),
]
