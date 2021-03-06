#coding=utf-8


"""
Django settings for stars project.

Generated by 'django-admin startproject' using Django 1.8.4.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import datetime
import djcelery
from oscar.defaults import *
from oscar import get_core_apps
from oscar import OSCAR_MAIN_TEMPLATE_DIR

from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse_lazy


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

location = lambda x: os.path.join(os.path.dirname(os.path.realpath(__file__)), x)

OSCAR_MAX_BASKET_QUANTITY_THRESHOLD = 100000
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'wb*9ayd)ql60%g$r5x*^@ae7(vc2_-)jl&nag3@6h@5#v59+b)'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

AUTH_PROFILE_MODULE = 'accounts.UserProfile'

ALLOWED_HOSTS = []

# celery

# celery settings and setup
# we use the redis backend
djcelery.setup_loader()
# setting to make django-celery use redis for the task store
# this should be the redis-togo url on heroku, which would be an environment variable
# BROKER_URL = os.environ.get('REDISTOGO_URL')
BROKER_URL = "redis://localhost:6379/0"

# force celery to save the task results (for testing only so we can see what the tasks are doing)
# this should be the redis-togo setting on heroku
CELERY_RESULT_BACKEND = os.environ.get('REDISTOGO_URL')


# force celery to to run tasks locally and syncronously during tests, set your environment variable to True
CELERY_ALWAYS_EAGER = os.environ.get('CELERY_ALWAYS_EAGER', True)

TEST_RUNNER = 'djcelery.contrib.test_runner.CeleryTestSuiteRunner'


# 我的账户首页--账户资产
OSCAR_ACCOUNTS_REDIRECT_URL = 'customer:assets'

OSCAR_DASHBOARD_DEFAULT_ACCESS_FUNCTION = 'stars.apps.dashboard.nav.default_access_fn'

PERMISSION_URL_DICT = {
    'dashboard:index': ['dashboard_admin'],
    'dashboard:catalogue-product-list': ['dashboard_admin'],
    'dashboard:catalogue-class-list': ['dashboard_admin'],
    'dashboard:catalogue-category-list': ['dashboard_admin'],
    'dashboard:partner-list': ['dashboard_admin'],
    'dashboard:user-list': ['dashboard_admin'],
    'dashboard:ad-rolling_ad-list': ['dashboard_admin'],
    'dashboard:users-index': ['dashboard_admin'],
    'dashboard:permission-group-list': [u'dashboard_admin'],
    'dashboard:business-product-list': ['dashboard_admin','member_unit'],
    'dashboard:business-stockenter-deal-list': ['dashboard_admin','member_unit'],
    'dashboard:storeincome-list': ['dashboard_admin','member_unit'],
    'dashboard:pickup-apply-list': ['dashboard_admin', 'member_unit'],
    'dashboard:business-pickupaddr-list': ['dashboard_admin', 'member_unit'],
    'dashboard:pickup-outstore-list': ['dashboard_admin', 'member_unit'],
    'dashboard:product-quotation-list': ['dashboard_admin','member_unit'],
    'dashboard:business-product-store-list': ['dashboard_admin', 'trader'],
    'dashboard:business-sale-list': ['dashboard_admin','member_unit'],
    'dashboard:business-profit-list': ['dashboard_admin','member_unit'],
    'dashboard:business-balance-list': ['dashboard_admin','member_unit'],
    'dashboard:pickup-store-list': ['dashboard_admin', 'warehouse_staff'],
    'dashboard:pickupaddr-pickup-apply-list': ['dashboard_admin', 'warehouse_staff'],
    'dashboard:store-income-apply-list': ['dashboard_admin', 'warehouse_staff'],
    'dashboard:store-income-list': ['dashboard_admin', 'warehouse_staff','member_unit'],
    'dashboard:store-income-update': ['dashboard_admin', 'warehouse_staff'],
    'dashboard:store-income-create': ['dashboard_admin', 'warehouse_staff'],
    'dashboard:pickup-apply-pickup-list': ['dashboard_admin', 'warehouse_staff'],
    'dashboard:pickup-apply-express-list': ['dashboard_admin', 'warehouse_staff'],
    'dashboard:pickup-statistics-list': ['dashboard_admin', 'warehouse_staff'],
    'dashboard:staticpage-list': ['dashboard_admin'],
    'dashboard:partneruser-list': ['dashboard_admin','member_unit'],
    'dashboard:express-send-list': ['dashboard_admin','member_unit'],
    'dashboard:trader-product-list': ['dashboard_admin', 'trader'],
    'dashboard:trader-sale-list': ['dashboard_admin', 'trader'],
    'dashboard:commission-query-list': ['dashboard_admin',],
    'dashboard:commission-query-all-list': ['dashboard_admin',],
    'dashboard:tradecomplete-query-list': ['dashboard_admin',],
    'dashboard:tradecomplete-query-all-list': ['dashboard_admin',],
    'dashboard:hold-product-list': ['dashboard_admin',],
    'dashboard:store-product-list': ['dashboard_admin',],
    'dashboard:store-product-all-list': ['dashboard_admin',],
    'dashboard:capital-query-list': ['dashboard_admin',],
    'dashboard:capital-query-all-list': ['dashboard_admin',],
}

OSCAR_DASHBOARD_NAVIGATION = [
    # dashboard_admin
    {
        'label': _(u'平台管理'),
        'url_name': 'dashboard:index',
    },
    {
        'label': _(u'商品管理'),
        'children': [
            {
                'label': _(u'商品'),
                'url_name': 'dashboard:catalogue-product-list',
            },
            {
                'label': _('Product Types'),
                'url_name': 'dashboard:catalogue-class-list',
            },
            {
                'label': _('Categories'),
                'url_name': 'dashboard:catalogue-category-list',
            },
        ]
    },
    {
        'label': _(u'权限管理'),
        'children': [
            {
                'label': _(u'用户管理'),
                'url_name': 'dashboard:user-list',
            },
            {
                'label': _(u'用户权限配置'),
                'url_name': 'dashboard:user-list',
            }
        ]
    },
    {
        'label': _(u'广告设置'),
        'url_name': 'dashboard:ad-rolling_ad-list',
    },
    {
        'label': _(u'公告管理'),
        'url_name': 'dashboard:staticpage-list',
    },
    {
        'label': _(u'风控管理'),
        'children': [
            {
                'label': _(u'交易挂起与释放'),
                'url_name': 'dashboard:users-index',
            },
            {
                'label': _(u'交易时间调整'),
                'url_name': 'dashboard:users-index',
            },
            {
                'label': _(u'商品挂起与释放'),
                'url_name': 'dashboard:users-index',
            },
            {
                'label': _(u'终端用户状态控制'),
                'url_name': 'dashboard:users-index',
            },
        ]
    },
    {
        'label': _(u'当日数据查询'),
        'children': [
            {
                'label': _(u'委托查询'),
                'url_name': 'dashboard:commission-query-list',
            },
            {
                'label': _(u'成交查询'),
                'url_name': 'dashboard:tradecomplete-query-list',
            },
            {
                'label': _(u'持有查询'),
                'url_name': 'dashboard:hold-product-list',
            },
            {
                'label': _(u'存货查询'),
                'url_name': 'dashboard:store-product-list',
            },
            {
                'label': _(u'资金查询'),
                'url_name': 'dashboard:capital-query-list',
            },
            {
                'label': _(u'用户综合查询'),
                'url_name': 'dashboard:users-index',
            },
            {
                'label': _(u'出入金查询'),
                'url_name': 'dashboard:users-index',
            },
        ]
    },
        {
        'label': _(u'历史数据查询'),
        'children': [
            {
                'label': _(u'交易商结算'),
                'url_name': 'dashboard:users-index',
            },
            {
                'label': _(u'委托查询'),
                'url_name': 'dashboard:commission-query-all-list',
            },
            {
                'label': _(u'成交查询'),
                'url_name': 'dashboard:tradecomplete-query-all-list',
            },
            {
                'label': _(u'存货查询'),
                'url_name': 'dashboard:store-product-all-list',
            },
            {
                'label': _(u'库存明细'),
                'url_name': 'dashboard:users-index',
            },
            {
                'label': _(u'盈亏查询'),
                'url_name': 'dashboard:users-index',
            },
            {
                'label': _(u'用户综合查询'),
                'url_name': 'dashboard:users-index',
            },
            {
                'label': _(u'出入金查询'),
                'url_name': 'dashboard:users-index',
            },
            {
                'label': _(u'资金查询'),
                'url_name': 'dashboard:capital-query-all-list',
            },
        ]
    },
    {
        'label': _(u'会员单位管理'),
        'children': [
            {
                'label': _(u'会员单位信息录入'),
                'url_name': 'dashboard:partner-list',
            },
            {
                'label': _(u'交易员管理'),
                'url_name': 'dashboard:users-index',
            },
        ]
    },
    {
        'label': _(u'自提点管理'),
        'url_name': 'dashboard:users-index',
    },
    # member_unit
    {
        'label': _(u'商品查询'),
        'url_name': 'dashboard:business-product-list',
    },
    {
        'label': _(u'销售信息查询'),
        'url_name': 'dashboard:business-sale-list',
    },
    {
        'label': _(u'销售额/利润查询'),
        'url_name': 'dashboard:business-profit-list',
    },
    {
        'label': _(u'会员单位自提点管理'),
        'children': [
            {
                'label': _(u'发货办理'),
                'url_name': 'dashboard:storeincome-list',
            },
            {
                'label': _(u'入库管理'),
                'url_name': 'dashboard:store-income-list',
            },
            {
                'label': _(u'库存查询'),
                'url_name': 'dashboard:business-pickupaddr-list',
            },
            {
                'label': _(u'提货信息查询'),
                'url_name': 'dashboard:pickup-apply-list',
            },
            {
                'label': _(u'出库查询'),
                'url_name': 'dashboard:pickup-outstore-list',
            },
        ]
    },
    {
        'label': _(u'用户发货管理'),
        'url_name': 'dashboard:express-send-list',
    },
    {
        'label':_(u'库转交易管理'),
        'url_name': 'dashboard:business-stockenter-deal-list',
    },
    {
        'label': _(u'账户资金'),
        'children': [
            {
                'label': _(u'申请提现'),
                'url_name': 'dashboard:storeincome-list',
            },
            ]
    },
    {
        'label':_(u'用户查询'),
        'url_name': 'dashboard:partneruser-list',
    },
    # trader
    {
        'label': _(u'交易员销售信息查询'),
        'url_name': 'dashboard:trader-sale-list',
    },
    {
        'label': _(u'关联商品查询'),
        'url_name': 'dashboard:trader-product-list',
    },
    {
        'label': _(u'库转交易'),
        'url_name': 'dashboard:business-product-store-list',
    },
    # warehouse_staff
    {
        'label': _(u'入库办理'),
        'url_name': 'dashboard:store-income-apply-list',
    },
    {
        'label': _(u'仓库数据查询'),
        'children': [
            {
                'label': _(u'申请提货查询'),
                'url_name': 'dashboard:pickupaddr-pickup-apply-list',
            },
            {
                'label': _(u'库存统计'),
                'url_name': 'dashboard:pickup-store-list',
            },
            {
                'label': _(u'提货统计'),
                'url_name': 'dashboard:pickup-statistics-list',
            },
        ]
    },
    {
        'label': _(u'出库办理'),
        'url_name': 'dashboard:pickup-apply-pickup-list',
    },
    {
        'label': _(u'库容登记'),
        'url_name': 'dashboard:users-index',
    },
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sites',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.flatpages',
    'compressor',
    'ckeditor',
    'djcelery',
    'ckeditor_uploader',
    'captcha',
    'widget_tweaks',
    'rest_framework',
    'qrcode',
] + get_core_apps([
    'stars.apps.basket',
    'stars.apps.catalogue',
    'stars.apps.partner',
    'stars.apps.customer',
    'stars.apps.dashboard',
    'stars.apps.promotions',
    'stars.apps.dashboard.ad',
    'stars.apps.dashboard.catalogue',
    'stars.apps.dashboard.partners',
    'stars.apps.dashboard.permission',
    'stars.apps.dashboard.pickup_admin',
    'stars.apps.dashboard.business',
    'stars.apps.dashboard.dataquery',
    'stars.apps.address',
    'stars.apps.wishlists',
])
INSTALLED_APPS += [
    'stars',
    'stars.apps.accounts',
    'stars.apps.ad',
    'stars.apps.public',
    'stars.apps.commission',
    'stars.apps.customer.safety',
    'stars.apps.customer.assets',
    'stars.apps.customer.receiving_address',
    'stars.apps.customer.stock',
    'stars.apps.customer.userpickup',
    'stars.apps.tradingcenter',
    'stars.apps.platform',
    'stars.apps.pickup_admin',
    'stars.apps.helper',
    'stars.apps.api',
    'stars.apps.dashboard.staticpages',
    'stars.apps.customer.finance',
    'stars.apps.mobile',
]

SITE_ID = 1

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',

    'oscar.apps.basket.middleware.BasketMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'stars.apps.accounts.role_front_check_middleware.RoleFrontCheckMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'oscar.apps.customer.auth_backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
)

#
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
    ),
}

JWT_AUTH = {
    'JWT_ENCODE_HANDLER':
    'rest_framework_jwt.utils.jwt_encode_handler',

    'JWT_DECODE_HANDLER':
    'rest_framework_jwt.utils.jwt_decode_handler',

    'JWT_PAYLOAD_HANDLER':
    'rest_framework_jwt.utils.jwt_payload_handler',

    'JWT_PAYLOAD_GET_USER_ID_HANDLER':
    'rest_framework_jwt.utils.jwt_get_user_id_from_payload_handler',

    'JWT_RESPONSE_PAYLOAD_HANDLER':
    'rest_framework_jwt.utils.jwt_response_payload_handler',

    'JWT_SECRET_KEY': SECRET_KEY,
    'JWT_ALGORITHM': 'HS256',
    'JWT_VERIFY': True,
    'JWT_VERIFY_EXPIRATION': True,
    'JWT_LEEWAY': 0,
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=1),
    'JWT_AUDIENCE': None,
    'JWT_ISSUER': None,

    'JWT_ALLOW_REFRESH': False,
    'JWT_REFRESH_EXPIRATION_DELTA': datetime.timedelta(days=7),

    'JWT_AUTH_HEADER_PREFIX': 'JWT',
}

ROOT_URLCONF = 'stars.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            location('templates'),
            OSCAR_MAIN_TEMPLATE_DIR,
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                'oscar.apps.search.context_processors.search_form',
                'oscar.apps.promotions.context_processors.promotions',
                'oscar.apps.checkout.context_processors.checkout',
                'oscar.apps.customer.notifications.context_processors.notifications',
                'oscar.core.context_processors.metadata',
            ],
        },
    },
]

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
    },
}

WSGI_APPLICATION = 'stars.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'stars',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': '127.0.0.1',
        'PORT': '5432',
        'ATOMIC_REQUESTS': True,
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'zh-CN'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = location('site_static')
STATICFILES_DIRS = (
    location('static'),
)

MEDIA_URL = '/media/'
MEDIA_ROOT = location('media')

LOCALE_PATHS = (
    location('locale'),
)

FINANCE_ROOT = location('finance_files')

AVATAR_ROOT = 'avatar'
DEFAULT_AVATAR = '/static/images/avatar.jpg'

CKEDITOR_UPLOAD_PATH = "ckeditor/"
CKEDITOR_RESTRICT_BY_USER = True
CKEDITOR_IMAGE_BACKEND = "pillow"
CKEDITOR_JQUERY_URL = '/static/libs/jquery/jquery-1.11.2.js'
CKEDITOR_CONFIGS = {
    'default': {
        'width': '95%',
        'removePlugins': 'stylesheetparser',
        'allowedContent': True,
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Styles', 'Format', 'Bold', 'Italic', 'Underline', 'Strike', 'SpellChecker', 'Undo', 'Redo'],
            ['Link','Unlink','Anchor'],
            ['JustifyLeft','JustifyCenter','JustifyRight','JustifyBlock'],
            ['Image', 'HorizontalRule'],
            ['TextColor', 'BGColor'],
            ['Smiley', 'SpecialChar'],
            ['Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', 'Source'],
        ],
    },
}

# mobile message accounts
MESSAGE_ACCOUNT = 'cf_xugn'
MESSAGE_PASSWORD = 'yzwyzw0906'
MESSAGE_URL = 'http://106.ihuyi.cn/webservice/sms.php?method=Submit'

OSCAR_DEFAULT_CURRENCY = 'RMB'

# 测试用 # FIXME # by lwj 20151016
OSCAR_FROM_EMAIL = 'bbt_server@163.com'
EMAIL_HOST = 'smtp.163.com'
EMAIL_HOST_USER = 'bbt_server'
EMAIL_HOST_PASSWORD = 'tac3322'
# end

# Mobile APP
APP_SECRET_KEY = 'aeb11af7b1750854cb6217cf33e1a5e48826369c1e255c33ff655ff3fc938e'

#django-redis
# CACHES = {
#     "default": {
#         "BACKEND": "django_redis.cache.RedisCache",
#         "LOCATION": "127.0.0.1:6379",
#         "OPTIONS": {
#             "CLIENT_CLASS": "django_redis.client.DefaultClient",
#         }
#     }
# }
#end

try:
    from stars.local_settings import *
except Exception as e:
    pass

try:
    from stars.solr_settings import *
except:
    pass
