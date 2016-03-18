充值
curl -H "Authorization: JWT eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InRpbWRvY3QiLCJ1c2VyX2lkIjo2LCJlbWFpbCI6IiIsImV4cCI6MTQ0ODAwNTI4OH0.z6ZTXp0WVZk0CxkLCeU137TSf-HloNQc3jQ3X_gEBO8" http://localhost:8000/api/recharge/ -d 'test=123&amount=10000'

获取余额
curl -H "Authorization: JWT eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InRpbWRvY3QiLCJ1c2VyX2lkIjo2LCJlbWFpbCI6IiIsImV4cCI6MTQ0ODAwNTI4OH0.z6ZTXp0WVZk0CxkLCeU137TSf-HloNQc3jQ3X_gEBO8" http://localhost:8000/api/recharge/ 


购买
curl -H "Authorization: JWT eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InRpbWRvY3QiLCJ1c2VyX2lkIjo2LCJlbWFpbCI6IiIsImV4cCI6MTQ0ODAwNTI4OH0.z6ZTXp0WVZk0CxkLCeU137TSf-HloNQc3jQ3X_gEBO8" http://localhost:8000/api/purchase/ -d 'product=215&c_type=1&price=1&quantity=1'


进货
curl -H "Authorization: JWT eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InRpbWRvY3QiLCJ1c2VyX2lkIjo2LCJlbWFpbCI6IiIsImV4cCI6MTQ0ODAwNTI4OH0.z6ZTXp0WVZk0CxkLCeU137TSf-HloNQc3jQ3X_gEBO8" http://localhost:8000/api/buy/ -d 'product=215&c_type=2&price=1&quantity=1'

出售
curl -H "Authorization: JWT eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InRpbWRvY3QiLCJ1c2VyX2lkIjo2LCJlbWFpbCI6IiIsImV4cCI6MTQ0ODAwNTI4OH0.z6ZTXp0WVZk0CxkLCeU137TSf-HloNQc3jQ3X_gEBO8" http://localhost:8000/api/sell/ -d 'product=215&c_type=1&price=1&quantity=1'

厂家出售
curl -H "Authorization: JWT eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InRpbWRvY3QiLCJ1c2VyX2lkIjo2LCJlbWFpbCI6IiIsImV4cCI6MTQ0ODAwNTI4OH0.z6ZTXp0WVZk0CxkLCeU137TSf-HloNQc3jQ3X_gEBO8" http://localhost:8000/api/factory/sell/ -d 'product=215&c_type=1&price=1&quantity=1'

商品行情和配置信息
curl -H "Authorization: JWT eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InRpbWRvY3QiLCJ1c2VyX2lkIjo2LCJlbWFpbCI6IiIsImV4cCI6MTQ0ODAwNTI4OH0.z6ZTXp0WVZk0CxkLCeU137TSf-HloNQc3jQ3X_gEBO8" http://localhost:8000/api/product/stock/ -d 'product_id=215'

获取商品id
curl -H "Authorization: JWT eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InRpbWRvY3QiLCJ1c2VyX2lkIjo2LCJlbWFpbCI6IiIsImV4cCI6MTQ0ODAwNTI4OH0.z6ZTXp0WVZk0CxkLCeU137TSf-HloNQc3jQ3X_gEBO8" http://localhost:8000/api/product/ids/ -X POST