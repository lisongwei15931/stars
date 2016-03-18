# -*- coding: utf-8 -*-
from __future__ import division

from django.contrib.auth.hashers import check_password
from django.db import transaction
from django.db.models import Q
import django.utils.timezone

from ab_service import AbService
from stars.apps.accounts.models import UserProfile
from stars.apps.commission.models import UserBank, UserBalance, UserMoneyChange, UserAssetDailyReport
from stars.apps.customer.finance.ab.common_const import AgriculturalBankTradeConstData
from stars.apps.customer.finance.ab.log import ab_log as logging
from stars.apps.customer.finance.ab.signal import received_file_names_done
from stars.apps.customer.finance.models import AbSignInContractLog, AbRescindContractLog, AbRechargeWithdrawHistory, \
    AbRechargeWithdrawLog
from stars.apps.customer.user_info.utils import get_user_id_from_inst_account_id
from stars.apps.tradingcenter.views import is_market_opening


class AbServerServiceBuilder(object):
    __service = {
        '20003': 'aa1',	  # 联通性检测
        '21001': 'aa2',	  # 签约
        '21004': 'aa3',	  # 解约
        '22001': 'aa4',	  # 入金申请
        '22002': 'aa5',	  # 出金申请
        '22005': 'aa6',	  # 入金审核查询
        '22006': 'aa7',	  # 出金审核查询
        '23004': 'aa8',	  # 查询市场资金余额
        '31101': 'aa9',	  # 文件生成通知
    }

    __service_trade_dict = {
        '20003': 'ConnectionCheckServerService',	  # 联通性检测
        '21001': 'SignContractFromBankServerService',	  # 签约
        '21004': 'RescindContractFromBankServerService',	  # 解约
        '22001': 'RechargeFromBankServerService',	  # 入金申请
        '22002': 'WithdrawFromBankServerService',	  # 出金申请
        '22005': 'RechargeFromBankStatusQueryServerService',	  # 入金审核查询
        '22006': 'WithdrawFromBankStatusQueryServerService',	  # 出金审核查询
        '23004': 'QueryMarketBalanceServerService',	  # 查询市场资金余额
        '31101': 'FilesCreationInformServerService',	  # 文件生成通知
    }

    @staticmethod
    def create_service(trade_no):
        if trade_no not in AbServerServiceBuilder.__service_trade_dict:
            raise ValueError

        return globals()[AbServerServiceBuilder.__service_trade_dict['trade_no']]()


class AbServerService(AbService):
    head_msg_type = 'B'
    trade_source = 'B'
    pass_exception_for_response = False

    def __init__(self, request,  suc_handler=None, error_handler=None):
        super(self.__class__, self).__init__(suc_handler, error_handler)
        self.__request = request

    def send_and_receive(self, data):
        return self.__request.sendall(data)

    def send(self, data):
        return self.__request.sendall(data)

    def receive(self, size):
        # TODO
        pass

    def do_event(self, data, keys=None):
        if not keys:
            pack_key, pin_key, mac_key = self.get_key()
        else:
            pack_key, pin_key, mac_key = keys

        header, cr_msg = self.split_header_msg(data)
        assert(header.trade_no == self.trade_no)

        # 不实现 by 农行赵工
        # # 检查mac
        # s = self.check_mac(cr_msg, header.mac, mac_key, pack_key, pin_key)
        # if s:
        #     return self.send(s)

        data = self.decrypt_recv_msg_body(cr_msg, len(cr_msg), pack_key, pin_key, mac_key)

        s = self.check_msg_text(data, pack_key, pin_key, mac_key)
        if s:
            return self.send(s)

        #检查通过
        r = self.do_work(data)

        try:
            self.response(r, pack_key, pin_key, mac_key)
        except Exception as e:
            if not self.__class__.pass_exception_for_response:
                raise e

        r = self.do_work_2(r)
        return r

    # 数据检查通过后，做业务相关工作
    def do_work(self, data):
        return data

    # 响应服务器后，做业务相关工作
    def do_work_2(self, data):
        pass

    def response(self, data, pack_key, pin_key, mac_key):
        t = self.make_data(data, pack_key, pin_key, mac_key)
        self.send(t)

    def close(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __del__(self):
        pass


class ConnectionCheckServerService(AbServerService):
    trade_no = '20003'
    version=''
    msg_template = '<root><sys><Version>{Version}</Version></sys>' \
                   '<pub><InstructionCode>{InstructionCode}</InstructionCode>' \
                   '<Code>{Code></Code><Info>{Info}</Info>' \
                    '<Date>{Date}</Date><Time>{Time}</Time><EntrustWay>{EntrustWay}</EntrustWay>' \
                    '<TradeSource>{TradeSource}</TradeSource>' \
                    '<InstNo>{InstNo}</InstNo></pub>' \
                    '<Serial>' \
                       '<SerialNo>{SerialNo}</SerialNo>' \
                       '<InstSerial>{InstSerial}</InstSerial>' \
                   '</Serial>' \
                    '</root>'

    must_exist_item = {'InstructionCode'}
    pass_exception_for_response = True

    def response(self, data, pack_key, pin_key, mac_key):
        # 成功
        code = '0000'  #
        m = {'InstructionCode': self.__class__.trade_no,  # 交易号
             'Version': '1.0',
             'TradeSource': self.trade_source,  # 交易发起方
             'InstNo': self.get_mch_id(),  # 市场编号
             'InstSerial': '',   # 市场流水号
             'Date': self.get_date(),
             'Time': self.get_time(),
             'Code': code,
             'Info': '',
             'SerialNo': data.get('SerialNo', ''),
             }
        t = self.make_data(m, pack_key, pin_key, mac_key)
        self.send_and_receive(t)

    def do_work(self, data):
        # 联通检查不做处理
        return data


class SignContractFromBankServerService(AbServerService):
    trade_no = '21001'
    version=''
    msg_template = '<root><sys><Version>{Version}</Version></sys>' \
                   '<pub>' \
                       '<InstructionCode>{InstructionCode}</InstructionCode>' \
                       '<Code>{Code></Code><Info>{Info}</Info>' \
                        '<Date>{Date}</Date><Time>{Time}</Time>' \
                        '<TradeSource>{TradeSource}</TradeSource>' \
                        '<InstNo>{InstNo}</InstNo>' \
                   '</pub>' \
                    '<Serial><SerialNo>{SerialNo}</SerialNo><InstSerial>{InstSerial}</InstSerial></Serial>' \
                    '<Business><BusiType>{BusiType}</BusiType><MoneyKind>{MoneyKind}</MoneyKind></Business>' \
                   '<Contract>' \
                        '<ClientNo>{ClientNo}</ClientNo><InstFundAcc>{InstFundAcc}</InstFundAcc>' \
                         '<InstBranch>{InstBranch}</InstBranch><InstBranchName></InstBranchName>    ' \
                        '<BankAccount></BankAccount>' \
                        '<InstFundBala>{InstFundBala}</InstFundBala>' \
                        '<Summary></Summary>'\
                   '</Contract>' \
                     '<Client>' \
                        '<CertType></CertType>' \
                        '<CertID></CertID>' \
                        '<ClientName></ClientName>' \
                   '</Client>' \
                    '<RESERVE><Reserve1></Reserve1><Reserve2></Reserve2></RESERVE>' \
                    '</root>'

    must_exist_item = {'InstructionCode',
                       'EntrustWay',
                       'TradeSource',
                       'SerialNo',
                       'InstNo',
                       'BusiType',
                       'MoneyKind',
                       'ClientNo',
                       'InstFundAcc',
                       'FundPassword',
                       'ClientName',
                       'CertType',
                       'CertID',
                       }

    def check_msg_text(self, data, pack_key, pin_key, mac_key):
        s = super(self.__class__, self).check_msg_text(data, pack_key, pin_key, mac_key)
        if s:
            return s

        # 2311	币种错
        # 2314	无此币种
        #
        # 2140	非交易时间
        # 不处理	银行流水号重复（2004）
        r = {'InstructionCode': self.__class__.trade_no,  # 交易号
             'TradeSource': self.trade_source,  # 交易发起方：银行
             'InstNo': self.get_mch_id(),  # 市场编号
             'InstSerial': self.create_ab_inst_serial(),   # 市场流水号
             'SerialNo': data.get('SerialNo', ''),
             'ClientNo': data.get('ClientNo', ''),
             'BusiType': data.get('BusiType', ''),
             'MoneyKind': data.get('MoneyKind', ''),
             'InstFundAcc': data.get('InstFuncAcc', ''),
             'InstBranch': AgriculturalBankTradeConstData.DEFAULT_INST_BRANCH,
             'Date': self.get_date(),
             'Time': self.get_time(),
             }

        if not is_market_opening():
            r['Code'] = '179001'  # 自定义code,不知是否有效
            r['Info'] = u'市场未开市，请开市后执行'

        elif not data.get('BankAccount'):   # 银行文档虽然不是必须项，市场需要
            r['Code'] = '178887'  # 参数错误
            r['Info'] = u'市场需要BankAccount'
            return r

        elif data.get('MoneyKind') != '01':   # 人民币
            r['Code'] = '172311'  # 参数错误
            r['Info'] = u'MoneyKind必须为人民币'
        elif data.get('BusiType') != '6':   # 人民币
            r['Code'] = '178887'  # 参数错误
            r['Info'] = u'BusiType必须为保证金'
        else:
            inst_fund_acc = data.get('InstFundAcc')
            try:
                user_profile = UserProfile.objects.get(user_id=get_user_id_from_inst_account_id(inst_fund_acc))
            except UserProfile.DoesNotExist:
                r['Code'] = '172011'  # 资金账户不存在
                r['Info'] = u'资金账户不存在'
            if not check_password(data.get('FundPassword'), user_profile.pay_pwd):
                r['Code'] = '172001'  #
                r['Info'] = u'资金账户密码错误'
            if user_profile.audit_status ==2:
                if user_profile.identification_card_number and user_profile.identification_card_number != data.get('CertID'):
                    r['Code'] = '172009'  #
                    r['Info'] = u'身份证号码不符'
                if user_profile.real_name and user_profile.real_name != data.get('ClientName'):
                    r['Code'] = '172047'  #
                    r['Info'] = u'账户姓名不符'

            if UserBank.objects.filter(Q(client_no=data['ClientNo']) | Q(bank_account=data['BankAccount']),
                                       is_rescinded=False).exists():
                r['Code'] = '172049'  #
                r['Info'] = u'资金账号与管理账号已建立对应关系'

        if r.get('Code'):
            t = self.make_data(r, pack_key, pin_key, mac_key)
            return t
        return None

    def do_work(self, data):
        # 改变用户状态  --- 不必改变，根据用户银行表即可判断用户签约状态
        # 保存用户银行帐号  UserBank
        # 记录日志  AbBankLog  id, 业务、发起方、状态、流水号，市场流水号、
        r = {'InstructionCode': self.__class__.trade_no,  # 交易号
             'TradeSource': self.trade_source,  # 交易发起方：银行
             'InstNo': self.get_mch_id(),  # 市场编号
             'InstSerial': self.create_ab_inst_serial(),   # 市场流水号
             'SerialNo': data.get('SerialNo', ''),
             'ClientNo': data.get('ClientNo', ''),
             'BusiType': data.get('BusiType', ''),
             'MoneyKind': data.get('MoneyKind', ''),
             'InstFundAcc': data.get('InstFuncAcc', ''),
             'InstBranch': AgriculturalBankTradeConstData.DEFAULT_INST_BRANCH,
             'Date': self.get_date(),
             'Time': self.get_time(),
             }

        inst_fund_acc = data.get('InstFundAcc')

        try:
            user_profile = UserProfile.objects.get(user_id=get_user_id_from_inst_account_id(inst_fund_acc))
            with transaction.atomic():
                d = AbSignInContractLog()
                d.user = user_profile.user
                d.status = 1

                d.trade_date = data.get('Date') if data.get('Date') else self.get_date()
                d.trade_time = data.get('Time') if data.get('Time') else self.get_time()
                d.inst_serial = r['InstSerial']
                d.serial_no = r['SerialNo']
                d.busi_type = r['BusiType']
                d.money_kind = r['MoneyKind']
                d.inst_func_acc = r['InstFundAcc']

                d.trade_source = self.trade_source

                d.bank_account = data['BankAccount']
                d.inst_func_acc = data['InstFundAcc']
                d.client_name = data['ClientNo']
                d.cert_id = data['CertId']
                d.cert_type = data['CertType']

                d.gender = data.get('Gender', '')
                d.agent_nationality = data.get('Nationality', '')
                d.tel_no = data.get('TelNo', '')
                d.fax_no = data.get('FaxNo', '')
                d.mobile = data.get('MobiNo', '')
                d.email = data.get('Email', '')
                d.address = data.get('Address', '')
                d.postcode = data.get('PostCode', '')

                d.agent_gender = data. get('AgentGender', '')
                d.agent_agent_nationality = data. get('AgentNationality', '')
                d.agent_tel_no = data. get('AgentTelNo', '')
                d.agent_fax_no = data. get('AgentFaxNo', '')
                d.agent_mobile = data. get('AgentMobiNo', '')
                d.agent_email = data. get('AgentEmail', '')
                d.agent_address = data. get('AgentAddress', '')
                d.agent_postcode = data. get('AgentPostCode', '')

                d.save()

                if user_profile.audit_status != 2:
                    user_profile.identification_card_number = d.cert_id
                    user_profile.real_name = d.client_name
                    user_profile.cert_type = 0 if d.cert_type == '110001' else 1

                    user_profile.save()

                UserBank(user=user_profile.user, bank_name=u'中国农业银行',
                                         bank_account=d.bank_account, tel=d.tel_no,
                                         client_no=d.client_no, client_name=d.client_name,
                                         is_enable=True, is_business_account=False if user_profile.cert_type==0 else True).save()
        except UserProfile.DoesNotExist:
            r['Code'] = '172011'  # 资金账户不存在
            r['Info'] = u'资金账户不存在'
            return r
        except Exception as e:
            logging.exception(e)
            r['Code'] = '178888'  #
            r['Info'] = u'系统错误，请稍后重试'
            return r

        try:
            r['InstFundBala'] = UserBalance.objects.get(user=user_profile.user).balance
        except Exception as e:
            pass
        r['Code'] = '170000'
        r['Info'] = u'签约成功'
        return r


# 解约
class RescindContractFromBankServerService(AbServerService):
    trade_no = '21004'
    version=''
    msg_template = '<root><sys><Version>{Version}</Version></sys>' \
                   '<pub>' \
                       '<InstructionCode>{InstructionCode}</InstructionCode>' \
                       '<Code>{Code></Code><Info>{Info}</Info>' \
                        '<Date>{Date}</Date><Time>{Time}</Time>' \
                        '<TradeSource>{TradeSource}</TradeSource>' \
                        '<InstNo>{InstNo}</InstNo>' \
                   '</pub>' \
                    '<Serial>' \
                       '<SerialNo>{SerialNo}</SerialNo>' \
                       '<InstSerial>{InstSerial}</InstSerial>' \
                   '</Serial>' \
                    '<Business><BusiType>{BusiType}</BusiType><MoneyKind>{MoneyKind}</MoneyKind></Business>' \
                   '<Contract>' \
                        '<ClientNo>{ClientNo}</ClientNo><InstFundAcc>{InstFundAcc}</InstFundAcc>' \
                        '<BankAccount></BankAccount>' \
                        '<Summary></Summary>'\
                   '</Contract>' \
                    '<Client>' \
                        '<CertType></CertType>' \
                        '<CertID></CertID>' \
                        '<ClientName></ClientName>' \
                   '</Client>' \
                    '<RESERVE><Reserve1></Reserve1><Reserve2></Reserve2></RESERVE>' \
                    '</root>'

    must_exist_item = {'InstructionCode',
                       'TradeSource',
                       'SerialNo',
                       'InstNo',
                       'BusiType',
                       'MoneyKind',
                       'ClientNo',
                       'InstFundAcc',
                       'FundPassword',
                       'ClientName',
                       'CertType',
                       'CertID',
                       }

    def check_msg_text(self, data, pack_key, pin_key, mac_key):
        s = super(self.__class__, self).check_msg_text(data, pack_key, pin_key, mac_key)
        if s:
            return s

        # 2311	币种错
        # 2314	无此币种
        #
        # 2140	非交易时间
        # 不处理	银行流水号重复（2004）

        r = {'InstructionCode': self.__class__.trade_no,  # 交易号
             'TradeSource': self.trade_source,  # 交易发起方：银行
             'InstNo': self.get_mch_id(),  # 市场编号
             'InstSerial': self.create_ab_inst_serial(),   # 市场流水号
             'SerialNo': data.get('SerialNo', ''),
             'ClientNo': data.get('ClientNo', ''),
             'BusiType': data.get('BusiType', ''),
             'MoneyKind': data.get('MoneyKind', ''),
             'InstFundAcc': data.get('InstFuncAcc', ''),
             'Date': self.get_date(),
             'Time': self.get_time(),
             }

        if not is_market_opening():
            r['Code'] = '179001'  # 自定义code,不知是否有效
            r['Info'] = u'市场未开市，请开市后执行'

        elif data.get('MoneyKind') != '01':   # 人民币
            r['Code'] = '172311'  # 参数错误
            r['Info'] = u'MoneyKind必须为人民币'
        elif data.get('BusiType') != '6':   # 人民币
            r['Code'] = '178887'  # 参数错误
            r['Info'] = u'BusiType必须为保证金'
        else:
            inst_fund_acc = data.get('InstFundAcc')
            try:
                user_profile = UserProfile.objects.get(user_id=get_user_id_from_inst_account_id(inst_fund_acc))
            except UserProfile.DoesNotExist:
                r['Code'] = '172011'  # 资金账户不存在
                r['Info'] = u'资金账户不存在'
            if not check_password(data.get('FundPassword'), user_profile.pay_pwd):
                r['Code'] = '172001'  #
                r['Info'] = u'资金账户密码错误'
            if user_profile.audit_status ==2:
                if user_profile.identification_card_number and user_profile.identification_card_number != data.get('CertID'):
                    r['Code'] = '172009'  #
                    r['Info'] = u'身份证号码不符'
                if user_profile.real_name and user_profile.real_name != data.get('ClientName'):
                    r['Code'] = '172047'  #
                    r['Info'] = u'账户姓名不符'

            if not UserBank.objects.filter(client_no=data['ClientNo'], is_rescinded=False).exists():
                r['Code'] = '172048'  #
                r['Info'] = u'资金账号与管理账号未建立对应关系'

            balance = UserBalance.objects.get(user=user_profile.user)
            if balance.balance != 0 or balance.locked !=0 :
                r['Code'] = '172034'  #
                r['Info'] = u'资金账户有余额，不允许解约'

            if UserMoneyChange.objects.filter(user=user_profile.user,trade_type_in=(1,2), created_date=django.utils.timezone.now().date()):
                 r['Code'] = '172038'  #
                 r['Info'] = u'当天有出入金业务发生,不允许解约'

        if r.get('Code'):
            t = self.make_data(r, pack_key, pin_key, mac_key)
            return t
        return None

    def do_work(self, data):
        # 改变用户状态  --- 不必改变，根据用户银行表即可判断用户签约状态
        # 保存用户银行帐号  UserBank
        # 记录日志  AbBankLog  id, 业务、发起方、状态、流水号，市场流水号、
        r = {'InstructionCode': self.__class__.trade_no,  # 交易号
             'TradeSource': self.trade_source,  # 交易发起方：银行
             'InstNo': self.get_mch_id(),  # 市场编号
             'InstSerial': self.create_ab_inst_serial(),   # 市场流水号
             'SerialNo': data.get('SerialNo', ''),
             'ClientNo': data.get('ClientNo', ''),
             'BusiType': data.get('BusiType', ''),
             'MoneyKind': data.get('MoneyKind', ''),
             'InstFundAcc': data.get('InstFuncAcc', ''),
             'Date': self.get_date(),
             'Time': self.get_time(),
             }

        inst_fund_acc = data.get('InstFundAcc')

        try:
            user_profile = UserProfile.objects.get(user_id=get_user_id_from_inst_account_id(inst_fund_acc))
            with transaction.atomic():
                d = AbRescindContractLog()
                d.user = user_profile.user
                d.status = 1

                d.trade_date = data.get('Date') if data.get('Date') else self.get_date()
                d.trade_time = data.get('Time') if data.get('Time') else self.get_time()
                d.trade_source = self.trade_source
                d.inst_serial = r['InstSerial']
                d.serial_no = r['SerialNo']
                d.busi_type = r['BusiType']
                d.money_kind = r['MoneyKind']
                d.inst_func_acc = r['InstFundAcc']
                d.client_no = r['ClientNo']

                d.trade_branch = r.get('TradeBranch', '')

                d.bank_account = data['BankAccount']
                d.inst_func_acc = data['InstFundAcc']
                d.client_name = data['ClientNo']
                d.cert_id = data['CertId']
                d.cert_type = data['CertType']

                d.save()

                UserBank.objects.filter(user=user_profile.user,  client_no=d.client_no, is_rescinded=False).update(is_rescinded=True)
        except UserProfile.DoesNotExist:
            r['Code'] = '172011'  # 资金账户不存在
            r['Info'] = u'资金账户不存在'
            return r
        except Exception as e:
            logging.exception(e)
            r['Code'] = '178888'  #
            r['Info'] = u'系统错误，请稍后重试'
            return r

        r['Code'] = '170000'
        r['Info'] = u'解约成功'
        return r


# 出金（充值）
class RechargeFromBankServerService(AbServerService):
    trade_no = '22002'
    version=''
    msg_template = '<root>' \
                   '<pub>' \
                       '<InstructionCode>{InstructionCode}</InstructionCode>' \
                       '<Code>{Code></Code><Info>{Info}</Info><SuccessFlag>{SuccessFlag}</SuccessFlag>' \
                        '<Date>{Date}</Date><Time>{Time}</Time>' \
                        '<TradeSource>{TradeSource}</TradeSource>' \
                        '<InstNo>{InstNo}</InstNo>' \
                   '</pub>' \
                    '<Serial><SerialNo>{SerialNo}</SerialNo><InstSerial>{InstSerial}</InstSerial></Serial>' \
                    '<Business>' \
                   '    <BusiType>{BusiType}</BusiType><MoneyKind>{MoneyKind}</MoneyKind><CashExCode>2</CashExCode>' \
                   '</Business>' \
                   '<Contract>' \
                        '<ClientNo>{ClientNo}</ClientNo><InstFundAcc>{InstFundAcc}</InstFundAcc>' \
                   '</Contract>' \
                    '<Transfer>' \
                        '<TransferAmount>{TransferAmount}</TransferAmount>' \
                        '<MoneyUsage></MoneyUsage>' \
                       '<MoneyUsageInfo></MoneyUsageInfo>' \
                    '</Transfer>' \
                    '<RESERVE><Reserve1></Reserve1><Reserve2></Reserve2></RESERVE>' \
                    '</root>'

    must_exist_item = {'InstructionCode',
                       'Date'
                       'TradeSource',
                       'SerialNo',
                       'InstNo',
                       'BusiType',
                       'MoneyKind',
                       'ClientNo',
                       'InstFundAcc',
                       'FundPassword',
                       'ClientName',
                       'TransferAmount',
                       }

    def check_msg_text(self, data, pack_key, pin_key, mac_key):
        s = super(self.__class__, self).check_msg_text(data, pack_key, pin_key, mac_key)
        if s:
            return s

        r = {'InstructionCode': self.__class__.trade_no,  # 交易号
             'TradeSource': self.trade_source,  # 交易发起方：银行
             'InstNo': self.get_mch_id(),  # 市场编号
             'InstSerial': self.create_ab_inst_serial(),   # 市场流水号
             'SerialNo': data.get('SerialNo', ''),
             'ClientNo': data.get('ClientNo', ''),
             'BusiType': data.get('BusiType', ''),
             'MoneyKind': data.get('MoneyKind', ''),
             'InstFundAcc': data.get('InstFuncAcc', ''),
             'Date': self.get_date(),
             'Time': self.get_time(),
             'TransferAmount': data.get('TransferAmount', '0'),
             'SuccessFlag': '',
             }

        if not is_market_opening():
            r['Code'] = '179001'  # 自定义code,不知是否有效
            r['Info'] = u'市场未开市，请开市后执行'

        elif data.get('MoneyKind') != '01':   # 人民币
            r['Code'] = '172311'  # 参数错误
            r['Info'] = u'MoneyKind必须为人民币'
        elif data.get('BusiType') != '6':   # 人民币
            r['Code'] = '178887'  # 参数错误
            r['Info'] = u'BusiType必须为保证金'
        elif AbRechargeWithdrawHistory.objects.filter(serial_no=r['SerialNo']).exists():
            r['Code'] = '172004'  # 资金账户不存在
            r['Info'] = u'银行流水号重复'
        else:
            inst_fund_acc = data.get('InstFundAcc')
            try:
                user_profile = UserProfile.objects.get(user_id=get_user_id_from_inst_account_id(inst_fund_acc))
            except UserProfile.DoesNotExist:
                r['Code'] = '172011'  # 资金账户不存在
                r['Info'] = u'资金账户不存在'
            else:
                if not check_password(data.get('FundPassword'), user_profile.pay_pwd):
                    r['Code'] = '172001'  #
                    r['Info'] = u'资金账户密码错误'
                if user_profile.audit_status ==2:
                    if user_profile.real_name and user_profile.real_name != data.get('ClientName'):
                        r['Code'] = '172047'  #
                        r['Info'] = u'账户姓名不符'

                if not UserBank.objects.filter(user=user_profile.user, client_no=data['ClientNo'], is_rescinded=False).exists():
                    r['Code'] = '172048'  #
                    r['Info'] = u'资金账号与管理账号未建立对应关系'

        if r.get('Code'):
            t = self.make_data(r, pack_key, pin_key, mac_key)
            return t
        return None

    def do_work(self, data):
        # 充值，改变用户账户余额
        #
        # 记录日志  AbBankLog  id, 业务、发起方、状态、流水号，市场流水号、金额

        r = {'InstructionCode': self.__class__.trade_no,  # 交易号
             'TradeSource': self.trade_source,  # 交易发起方：银行
             'InstNo': self.get_mch_id(),  # 市场编号
             'InstSerial': self.create_ab_inst_serial(),   # 市场流水号
             'SerialNo': data.get('SerialNo', ''),
             'ClientNo': data.get('ClientNo', ''),
             'BusiType': data.get('BusiType', ''),
             'MoneyKind': data.get('MoneyKind', ''),
             'InstFundAcc': data.get('InstFuncAcc', ''),
             'Date': self.get_date(),
             'Time': self.get_time(),
             'TransferAmount': data.get('TransferAmount', '0'),
             'SuccessFlag': '',
             }

        inst_fund_acc = data.get('InstFundAcc')

        try:
            user_profile = UserProfile.objects.get(user_id=get_user_id_from_inst_account_id(inst_fund_acc))

            with transaction.atomic():
                d = AbRechargeWithdrawLog()
                d.user = user_profile.user
                d.status = 1
                d.event = 1 #出金

                d.trade_date = data.get('Date') if data.get('Date') else self.get_date()
                d.trade_time = data.get('Time') if data.get('Time') else self.get_time()
                d.inst_serial = r['InstSerial']
                d.serial_no = r['SerialNo']

                d.trade_source = self.trade_source

                d.busi_type = r['BusiType']
                d.money_kind = r['MoneyKind']
                d.inst_func_acc = r['InstFundAcc']
                d.client_no = r['ClientNo']

                d.bank_account = data.get('bank_account', '')
                d.inst_func_acc = data['inst_fund_acc']
                d.client_name = data['client_name']
                d.transfer_amount = data['transfer_amount']

                d.cash_ex_code = data.get('CashExCode', '')
                d.money_usage = data.get('MoneyUsage', '')
                d.money_usage_info = data.get('MoneyUsageInfo', '')
                d.taster = data.get('Taster', '')
                d.broker = data.get('Broker', '')

                d.user_comment = data.get('comment', '')

                d.save()
                bank_name = UserBank.objects.get(user=user_profile.user, client_no=r['ClientNo'], is_rescinded=False).bank_name
                UserMoneyChange(user=user_profile.user, trade_type=1, status=2, price=float(d.transfer_amount),
                        money_bank=bank_name).custom_save()

                r['SuccessFlag'] = 'S'

        except UserProfile.DoesNotExist:
            r['Code'] = '172011'  # 资金账户不存在
            r['Info'] = u'资金账户不存在'
            return r
        except Exception as e:
            logging.exception(e)
            r['Code'] = '178888'  #
            r['Info'] = u'系统错误，请稍后重试'
            return r

        r['Code'] = '170000'
        r['Info'] = u'出金成功'
        return r


# 入金审核查询
class RechargeFromBankStatusQueryServerService(AbServerService):
    trade_no = '22006'
    version=''
    msg_template = '<root>' \
                   '<pub>' \
                       '<InstructionCode>{InstructionCode}</InstructionCode>' \
                       '<Code>{Code></Code><Info>{Info}</Info><SuccessFlag>{SuccessFlag}</SuccessFlag>' \
                        '<Date>{Date}</Date><Time>{Time}</Time>' \
                        '<TradeSource>B</TradeSource>' \
                        '<InstNo>{InstNo}</InstNo>' \
                   '</pub>' \
                    '<Serial><SerialNo>{SerialNo}</SerialNo><InstSerial>{InstSerial}</InstSerial></Serial>' \
                    '<Business><BusiType>{BusiType}</BusiType><MoneyKind>{MoneyKind}</MoneyKind></Business><CashExCode>2</CashExCode>' \
                   '<Contract>' \
                        '<ClientNo>{ClientNo}</ClientNo><InstFundAcc>{InstFundAcc}</InstFundAcc>' \
                   '</Contract>' \
                    '<Transfer>' \
                        '<TransferAmount>{TransferAmount}</TransferAmount>' \
                        '<MoneyUsage></MoneyUsage>' \
                       '<MoneyUsageInfo></MoneyUsageInfo>' \
                        '<InstPassStatus>{InstPassStatus}</InstPassStatus>' \
                   '</Transfer>' \
                    '<RESERVE><Reserve1></Reserve1><Reserve2></Reserve2></RESERVE>' \
                    '</root>'

    must_exist_item = {'InstructionCode',
                       'TradeSource',
                       'SerialNo',
                       'InstNo',
                       'BusiType',
                       'MoneyKind',
                       'ClientNo',
                       'InstFundAcc',
                       'FundPassword',
                       'TransferAmount',
                       'CashExCode',  # 汇钞标志
                       'OriSerial',   # 原交易流水号
                       }

    def check_msg_text(self, data, pack_key, pin_key, mac_key):
        s = super(self.__class__, self).check_msg_text(data, pack_key, pin_key, mac_key)
        if s:
            return s

        r = {'InstructionCode': self.__class__.trade_no,  # 交易号
             'TradeSource': self.trade_source,  # 交易发起方：银行
             'InstNo': self.get_mch_id(),  # 市场编号
             'InstSerial': self.create_ab_inst_serial(),   # 市场流水号
             'SerialNo': data.get('SerialNo', ''),
             'ClientNo': data.get('ClientNo', ''),
             'BusiType': data.get('BusiType', ''),
             'MoneyKind': data.get('MoneyKind', ''),
             'InstFundAcc': data.get('InstFuncAcc', ''),
             'Date': self.get_date(),
             'Time': self.get_time(),
             'TransferAmount': data.get('TransferAmount', '0'),
             'InstPassStatus': '',
             }

        # if not is_market_opening():
        #     r['Code'] = '179001'  # 自定义code,不知是否有效
        #     r['Info'] = u'市场未开市，请开市后执行'

        if data.get('MoneyKind') != '01':   # 人民币
            r['Code'] = '172311'  # 参数错误
            r['Info'] = u'MoneyKind必须为人民币'
        elif data.get('BusiType') != '6':   # 人民币
            r['Code'] = '178887'  # 参数错误
            r['Info'] = u'BusiType必须为保证金'
        else:
            inst_fund_acc = data.get('InstFundAcc')
            try:
                user_profile = UserProfile.objects.get(user_id=get_user_id_from_inst_account_id(inst_fund_acc))
            except UserProfile.DoesNotExist:
                r['Code'] = '172011'  # 资金账户不存在
                r['Info'] = u'资金账户不存在'
            else:
                if not check_password(data.get('FundPassword'), user_profile.pay_pwd):
                    r['Code'] = '172001'  #
                    r['Info'] = u'资金账户密码错误'
                if user_profile.audit_status ==2:
                    if user_profile.real_name and user_profile.real_name != data.get('ClientName'):
                        r['Code'] = '172047'  #
                        r['Info'] = u'账户姓名不符'

                if not UserBank.objects.filter(user=user_profile.user, client_no=data['ClientNo'], is_rescinded=False).exists():
                    r['Code'] = '172048'  #
                    r['Info'] = u'资金账号与管理账号未建立对应关系'

        if r.get('Code'):
            t = self.make_data(r, pack_key, pin_key, mac_key)
            return t
        return None

    def do_work(self, data):
        #
        # 记录日志  AbBankLog  id, 业务、发起方、状态、流水号，市场流水号、金额
        r = {'InstructionCode': self.__class__.trade_no,  # 交易号
             'TradeSource': self.trade_source,  # 交易发起方：银行
             'InstNo': self.get_mch_id(),  # 市场编号
             'InstSerial': self.create_ab_inst_serial(),   # 市场流水号
             'SerialNo': data.get('SerialNo', ''),
             'ClientNo': data.get('ClientNo', ''),
             'BusiType': data.get('BusiType', ''),
             'MoneyKind': data.get('MoneyKind', ''),
             'InstFundAcc': data.get('InstFuncAcc', ''),
             'Date': self.get_date(),
             'Time': self.get_time(),
             'TransferAmount': data.get('TransferAmount', '0'),
             'InstPassStatus': '',
             }

        user_id = get_user_id_from_inst_account_id(data.get('InstFundAcc'))

        try:
            l = AbRechargeWithdrawLog.objects.get(user_id=user_id, serial_no=data.get('OriSerial', ''), event=2)
            r['TransferAmount'] = l.transfer_amount
            if l.status == 1:
                r['InstPassStatus'] = 'S'
            elif l.status == 2:
                r['InstPassStatus'] = 'R'
            else:
                r['InstPassStatus'] = 'P'

        except AbRechargeWithdrawLog.DoesNotExist:
            r['Code'] = '172027'  # 资金账户不存在
            r['Info'] = u'原交易流水号不存在'
            return r
        except Exception as e:
            logging.exception(e)
            r['Code'] = '178888'  #
            r['Info'] = u'系统错误，请稍后重试'
            return r

        r['Code'] = '170000'
        r['Info'] = u'出金查询成功'
        return r


# 入金（提现）
class WithdrawFromBankServerService(AbServerService):
    trade_no = '22001'
    version=''
    msg_template = '<root>' \
                   '<pub>' \
                       '<InstructionCode>{InstructionCode}</InstructionCode>' \
                       '<Code>{Code></Code><Info>{Info}</Info>' \
                        '<Date>{Date}</Date><Time>{Time}</Time>' \
                        '<TradeSource>{TradeSource}</TradeSource>' \
                        '<InstNo>{InstNo}</InstNo>' \
                   '</pub>' \
                    '<Serial><SerialNo>{SerialNo}</SerialNo><InstSerial>{InstSerial}</InstSerial></Serial>' \
                    '<Business>' \
                   '    <BusiType>{BusiType}</BusiType><MoneyKind>{MoneyKind}</MoneyKind><CashExCode>2</CashExCode>' \
                   '</Business>' \
                   '<Contract>' \
                        '<ClientNo>{ClientNo}</ClientNo><InstFundAcc>{InstFundAcc}</InstFundAcc>' \
                   '</Contract>' \
                    '<Transfer>' \
                        '<TransferAmount>{TransferAmount}</TransferAmount>' \
                        '<MoneyUsage></MoneyUsage>' \
                       '<MoneyUsageInfo></MoneyUsageInfo>' \
                        '</Transfer>' \
                    '<RESERVE><Reserve1></Reserve1><Reserve2></Reserve2></RESERVE>' \
                    '</root>'

    must_exist_item = {'InstructionCode',
                       'Date'
                       'TradeSource',
                       'SerialNo',
                       'InstNo',
                       'BusiType',
                       'MoneyKind',
                       'ClientNo',
                       'InstFundAcc',
                       'FundPassword',
                       'ClientName',
                       'TransferAmount',
                       }

    def check_msg_text(self, data, pack_key, pin_key, mac_key):
        s = super(self.__class__, self).check_msg_text(data, pack_key, pin_key, mac_key)
        if s:
            return s

        # 2311	币种错
        # 2314	无此币种
        #
        # 2140	非交易时间
        # 不处理	银行流水号重复（2004）

        r = {'InstructionCode': self.__class__.trade_no,  # 交易号
             'TradeSource': self.trade_source,  # 交易发起方：银行
             'InstNo': self.get_mch_id(),  # 市场编号
             'InstSerial': self.create_ab_inst_serial(),   # 市场流水号
             'SerialNo': data.get('SerialNo', ''),
             'ClientNo': data.get('ClientNo', ''),
             'BusiType': data.get('BusiType', ''),
             'MoneyKind': data.get('MoneyKind', ''),
             'InstFundAcc': data.get('InstFuncAcc', ''),
             'Date': self.get_date(),
             'Time': self.get_time(),
             'TransferAmount': data.get('TransferAmount', '0'),
             }

        if not is_market_opening():
            r['Code'] = '179001'  # 自定义code,不知是否有效
            r['Info'] = u'市场未开市，请开市后执行'

        elif data.get('MoneyKind') != '01':   # 人民币
            r['Code'] = '172311'  # 参数错误
            r['Info'] = u'MoneyKind必须为人民币'
        elif data.get('BusiType') != '6':   # 人民币
            r['Code'] = '178887'  # 参数错误
            r['Info'] = u'BusiType必须为保证金'
        elif AbRechargeWithdrawHistory.objects.filter(serial_no=r['SerialNo']).exists():
            r['Code'] = '172004'  # 资金账户不存在
            r['Info'] = u'银行流水号重复'
        else:
            inst_fund_acc = data.get('InstFundAcc')
            try:
                user_profile = UserProfile.objects.get(user_id=get_user_id_from_inst_account_id(inst_fund_acc))
            except UserProfile.DoesNotExist:
                r['Code'] = '172011'  # 资金账户不存在
                r['Info'] = u'资金账户不存在'
            else:
                if not check_password(data.get('FundPassword'), user_profile.pay_pwd):
                    r['Code'] = '172001'  #
                    r['Info'] = u'资金账户密码错误'
                if user_profile.audit_status ==2:
                    if user_profile.real_name and user_profile.real_name != data.get('ClientName'):
                        r['Code'] = '172047'  #
                        r['Info'] = u'账户姓名不符'

                if not UserBank.objects.filter(user=user_profile.user, client_no=data['ClientNo'], is_rescinded=False).exists():
                    r['Code'] = '172048'  #
                    r['Info'] = u'资金账号与管理账号未建立对应关系'


        if r.get('Code'):
            t = self.make_data(r, pack_key, pin_key, mac_key)
            return t
        return None

    def do_work(self, data):
        # 充值，改变用户账户余额
        #
        # 记录日志  AbBankLog  id, 业务、发起方、状态、流水号，市场流水号、金额
        r = {'InstructionCode': self.__class__.trade_no,  # 交易号
             'TradeSource': self.trade_source,  # 交易发起方：银行
             'InstNo': self.get_mch_id(),  # 市场编号
             'InstSerial': self.create_ab_inst_serial(),   # 市场流水号
             'SerialNo': data.get('SerialNo', ''),
             'ClientNo': data.get('ClientNo', ''),
             'BusiType': data.get('BusiType', ''),
             'MoneyKind': data.get('MoneyKind', ''),
             'InstFundAcc': data.get('InstFuncAcc', ''),
             'Date': self.get_date(),
             'Time': self.get_time(),
             'TransferAmount': data.get('TransferAmount', '0'),
             }

        inst_fund_acc = data.get('InstFundAcc')

        try:
            user_profile = UserProfile.objects.get(user_id=get_user_id_from_inst_account_id(inst_fund_acc))
            transfer_amount = float(data['TransferAmount'])
            with transaction.atomic():
                balance = UserBalance.objects.select_for_update().get(user=user_profile.user)
                if balance.balance < transfer_amount:
                    r['Code'] = '172002'  #
                    r['Info'] = u'资金账户余额不足'
                    return r
                d = AbRechargeWithdrawLog()
                d.user = user_profile.user
                d.status = 1
                d.event = 2     # 入金

                d.trade_date = data.get('Date') if data.get('Date') else self.get_date()
                d.trade_time = data.get('Time') if data.get('Time') else self.get_time()
                d.inst_serial = r['InstSerial']
                d.serial_no = r['SerialNo']

                d.trade_source = self.trade_source

                d.busi_type = r['BusiType']
                d.money_kind = r['MoneyKind']
                d.inst_func_acc = r['InstFundAcc']
                d.client_no = r['ClientNo']

                d.bank_account = data.get('bank_account', '')
                d.inst_func_acc = data['inst_fund_acc']
                d.client_name = data['client_name']
                d.transfer_amount = transfer_amount

                d.cash_ex_code = data.get('CashExCode', '')
                d.money_usage = data.get('MoneyUsage', '')
                d.money_usage_info = data.get('MoneyUsageInfo', '')

                d.user_comment = data.get('comment', '')

                d.save()
                bank_name = UserBank.objects.get(user=user_profile.user, client_no=r['ClientNo'], is_rescinded=False).bank_name
                UserMoneyChange(user=user_profile.user, trade_type=2, status=2, price=transfer_amount,
                        money_bank=bank_name).custom_save()


        except UserProfile.DoesNotExist:
            r['Code'] = '172011'  # 资金账户不存在
            r['Info'] = u'资金账户不存在'
            return r
        except Exception as e:
            logging.exception(e)
            r['Code'] = '178888'  #
            r['Info'] = u'系统错误，请稍后重试'
            return r

        r['Code'] = '170000'
        r['Info'] = u'出金成功'
        return r


# 入金审核查询
class WithdrawFromBankStatusQueryServerService(AbServerService):
    trade_no = '22005'
    version=''
    msg_template = '<root>' \
                   '<pub>' \
                       '<InstructionCode>{InstructionCode}</InstructionCode>' \
                       '<Code>{Code></Code><Info>{Info}</Info><SuccessFlag>{SuccessFlag}</SuccessFlag>' \
                        '<Date>{Date}</Date><Time>{Time}</Time>' \
                        '<TradeSource>B</TradeSource>' \
                        '<InstNo>{InstNo}</InstNo>' \
                   '</pub>' \
                    '<Serial><SerialNo>{SerialNo}</SerialNo><InstSerial>{InstSerial}</InstSerial></Serial>' \
                    '<Business><BusiType>{BusiType}</BusiType><MoneyKind>{MoneyKind}</MoneyKind></Business><CashExCode>2</CashExCode>' \
                   '<Contract>' \
                        '<ClientNo>{ClientNo}</ClientNo><InstFundAcc>{InstFundAcc}</InstFundAcc>' \
                   '</Contract>' \
                    '<Transfer>' \
                        '<TransferAmount>{TransferAmount}</TransferAmount>' \
                        '<MoneyUsage></MoneyUsage>' \
                       '<MoneyUsageInfo></MoneyUsageInfo>' \
                        '<InstPassStatus>{InstPassStatus}</InstPassStatus>' \
                   '</Transfer>' \
                    '<RESERVE><Reserve1></Reserve1><Reserve2></Reserve2></RESERVE>' \
                    '</root>'

    must_exist_item = {'InstructionCode',
                       'TradeSource',
                       'SerialNo',
                       'InstNo',
                       'BusiType',
                       'MoneyKind',
                       'ClientNo',
                       'InstFundAcc',
                       'FundPassword',
                       'TransferAmount',
                       'CashExCode',  # 汇钞标志
                       'OriSerial',   # 原交易流水号
                       }

    def check_msg_text(self, data, pack_key, pin_key, mac_key):
        s = super(self.__class__, self).check_msg_text(data, pack_key, pin_key, mac_key)
        if s:
            return s

        r = {'InstructionCode': self.__class__.trade_no,  # 交易号
             'TradeSource': self.trade_source,  # 交易发起方：银行
             'InstNo': self.get_mch_id(),  # 市场编号
             'InstSerial': self.create_ab_inst_serial(),   # 市场流水号
             'SerialNo': data.get('SerialNo', ''),
             'ClientNo': data.get('ClientNo', ''),
             'BusiType': data.get('BusiType', ''),
             'MoneyKind': data.get('MoneyKind', ''),
             'InstFundAcc': data.get('InstFuncAcc', ''),
             'Date': self.get_date(),
             'Time': self.get_time(),
             'TransferAmount': data.get('TransferAmount', '0'),
             'InstPassStatus': '',
             }

        # if not is_market_opening():
        #     r['Code'] = '179001'  # 自定义code,不知是否有效
        #     r['Info'] = u'市场未开市，请开市后执行'

        if data.get('MoneyKind') != '01':   # 人民币
            r['Code'] = '172311'  # 参数错误
            r['Info'] = u'MoneyKind必须为人民币'
        elif data.get('BusiType') != '6':   # 人民币
            r['Code'] = '178887'  # 参数错误
            r['Info'] = u'BusiType必须为保证金'
        else:
            inst_fund_acc = data.get('InstFundAcc')
            try:
                user_profile = UserProfile.objects.get(user_id=get_user_id_from_inst_account_id(inst_fund_acc))
            except UserProfile.DoesNotExist:
                r['Code'] = '172011'  # 资金账户不存在
                r['Info'] = u'资金账户不存在'
            else:
                if not check_password(data.get('FundPassword'), user_profile.pay_pwd):
                    r['Code'] = '172001'  #
                    r['Info'] = u'资金账户密码错误'
                if user_profile.audit_status ==2:
                    if user_profile.real_name and user_profile.real_name != data.get('ClientName'):
                        r['Code'] = '172047'  #
                        r['Info'] = u'账户姓名不符'

                if not UserBank.objects.filter(user=user_profile.user, client_no=data['ClientNo'], is_rescinded=False).exists():
                    r['Code'] = '172048'  #
                    r['Info'] = u'资金账号与管理账号未建立对应关系'

        if r.get('Code'):
            t = self.make_data(r, pack_key, pin_key, mac_key)
            return t
        return None

    def do_work(self, data):
        #
        # 记录日志  AbBankLog  id, 业务、发起方、状态、流水号，市场流水号、金额
        r = {'InstructionCode': self.__class__.trade_no,  # 交易号
             'TradeSource': self.trade_source,  # 交易发起方：银行
             'InstNo': self.get_mch_id(),  # 市场编号
             'InstSerial': self.create_ab_inst_serial(),   # 市场流水号
             'SerialNo': data.get('SerialNo', ''),
             'ClientNo': data.get('ClientNo', ''),
             'BusiType': data.get('BusiType', ''),
             'MoneyKind': data.get('MoneyKind', ''),
             'InstFundAcc': data.get('InstFuncAcc', ''),
             'Date': self.get_date(),
             'Time': self.get_time(),
             'TransferAmount': data.get('TransferAmount', '0'),
             'InstPassStatus': '',
             }

        user_id = get_user_id_from_inst_account_id(data.get('InstFundAcc'))

        try:
            l = AbRechargeWithdrawLog.objects.get(user_id=user_id, serial_no=data.get('OriSerial', ''), event=1)
            r['TransferAmount'] = l.transfer_amount
            if l.status == 1:
                r['InstPassStatus'] = 'S'
            elif l.status == 2:
                r['InstPassStatus'] = 'R'
            else:
                r['InstPassStatus'] = 'P'

        except AbRechargeWithdrawLog.DoesNotExist:
            r['Code'] = '172027'  #
            r['Info'] = u'原交易流水号不存在'
            return r
        except Exception as e:
            logging.exception(e)
            r['Code'] = '178888'  #
            r['Info'] = u'系统错误，请稍后重试'
            return r

        r['Code'] = '170000'
        r['Info'] = u'出金查询成功'
        return r


# 查询市场余额
class QueryMarketBalanceServerService(AbServerService):
    trade_no = '23004'
    msg_template = '<root>' \
                   '<pub>' \
                       '<InstructionCode>{InstructionCode}</InstructionCode>' \
                       '<Code>{Code></Code><Info>{Info}</Info>' \
                        '<Date>{Date}</Date><Time>{Time}</Time>' \
                        '<TradeSource>{TradeSource}</TradeSource>' \
                        '<InstNo>{InstNo}</InstNo>' \
                        '<RTBalance>{RTBalance}</RTBalance><CurrentBalance>{CurrentBalance}</CurrentBalance>' \
                        '<AvailableBalance>{AvailableBalance}</AvailableBalance><FetchBalance>{FetchBalance}</FetchBalance>' \
                        '<MarginBalance></MarginBalance><LoanBalance></LoanBalance>' \
                        '<FloatProfit></FloatProfit><OtherBalance></OtherBalance>' \
                   '</pub>' \
                    '<Serial><SerialNo>{SerialNo}</SerialNo><InstSerial>{InstSerial}</InstSerial></Serial>' \
                    '<Business><BusiType>{BusiType}</BusiType><MoneyKind>{MoneyKind}</MoneyKind></Business>' \
                   '<Contract>' \
                        '<ClientNo>{ClientNo}</ClientNo><InstFundAcc>{InstFundAcc}</InstFundAcc>' \
                   '</Contract>' \
                    '</root>'

    must_exist_item = {'InstructionCode',
                       'TradeSource',
                       'SerialNo',
                       'InstNo',
                       'BusiType',
                       'MoneyKind',
                       'ClientNo',
                       'InstFundAcc',
                       'FundPassword',
                       }

    def check_msg_text(self, data, pack_key, pin_key, mac_key):
        s = super(self.__class__, self).check_msg_text(data, pack_key, pin_key, mac_key)
        if s:
            return s

        # 2311	币种错
        # 2314	无此币种
        #
        # 2140	非交易时间
        # 不处理	银行流水号重复（2004）

        r = {'InstructionCode': self.__class__.trade_no,  # 交易号
             'TradeSource': self.trade_source,  # 交易发起方：银行
             'InstNo': self.get_mch_id(),  # 市场编号
             'InstSerial': self.create_ab_inst_serial(),   # 市场流水号
             'SerialNo': data.get('SerialNo', ''),
             'ClientNo': data.get('ClientNo', ''),
             'BusiType': data.get('BusiType', ''),
             'MoneyKind': data.get('MoneyKind', ''),
             'InstFundAcc': data.get('InstFuncAcc', ''),
             'Date': self.get_date(),
             'Time': self.get_time(),
             'TransferAmount': data.get('TransferAmount', '0'),
             }

        # if not is_market_opening():
        #     r['Code'] = '179001'  # 自定义code,不知是否有效
        #     r['Info'] = u'市场未开市，请开市后执行'

        if data.get('MoneyKind') != '01':   # 人民币
            r['Code'] = '172311'  # 参数错误
            r['Info'] = u'MoneyKind必须为人民币'
        elif data.get('BusiType') != '6':   # 人民币
            r['Code'] = '178887'  # 参数错误
            r['Info'] = u'BusiType必须为保证金'
        # elif AbRechargeWithdrawHistory.objects.filter(serial_no=r['SerialNo']).exists():
        #     r['Code'] = '172004'  # 资金账户不存在
        #     r['Info'] = u'银行流水号重复'
        else:
            inst_fund_acc = data.get('InstFundAcc')
            try:
                user_profile = UserProfile.objects.get(user_id=get_user_id_from_inst_account_id(inst_fund_acc))
            except UserProfile.DoesNotExist:
                r['Code'] = '172011'  # 资金账户不存在
                r['Info'] = u'资金账户不存在'
            else:
                if not check_password(data.get('FundPassword'), user_profile.pay_pwd):
                    r['Code'] = '172001'  #
                    r['Info'] = u'资金账户密码错误'
                if user_profile.audit_status ==2:
                    if user_profile.real_name and user_profile.real_name != data.get('ClientName'):
                        r['Code'] = '172047'  #
                        r['Info'] = u'账户姓名不符'

                if not UserBank.objects.filter(user=user_profile.user, client_no=data['ClientNo'], is_rescinded=False).exists():
                    r['Code'] = '172048'  #
                    r['Info'] = u'资金账号与管理账号未建立对应关系'


        if r.get('Code'):
            t = self.make_data(r, pack_key, pin_key, mac_key)
            return t
        return None

    def do_work(self, data):
        # 充值，改变用户账户余额
        #
        # 记录日志  AbBankLog  id, 业务、发起方、状态、流水号，市场流水号、金额
        r = {'InstructionCode': self.__class__.trade_no,  # 交易号
             'TradeSource': self.trade_source,  # 交易发起方：银行
             'InstNo': self.get_mch_id(),  # 市场编号
             'InstSerial': self.create_ab_inst_serial(),   # 市场流水号
             'SerialNo': data.get('SerialNo', ''),
             'ClientNo': data.get('ClientNo', ''),
             'BusiType': data.get('BusiType', ''),
             'MoneyKind': data.get('MoneyKind', ''),
             'InstFundAcc': data.get('InstFuncAcc', ''),
             'Date': self.get_date(),
             'Time': self.get_time(),
             }

        inst_fund_acc = data.get('InstFundAcc')

        try:
            user_id = get_user_id_from_inst_account_id(inst_fund_acc)
            balance = UserBalance.objects.select_for_update().get(user_id=user_id)
            r['RTBalance'] = r['CurrentBalance'] = balance.balance
            report = UserAssetDailyReport.objects.filter(user_id=user_id).latest('created_date')
            if not report:
                r['AvailableBalance'] = balance.balance
                r['FetchBalance'] = balance.balance
            else:
                r['AvailableBalance'] = report.can_use_amount
                r['FetchBalance'] = report.can_out_amount
        except Exception as e:
            logging.exception(e)
            r['Code'] = '178888'  #
            r['Info'] = u'系统错误，请稍后重试'
            return r

        r['Code'] = '170000'
        r['Info'] = u'查询余额成功'
        return r


# 文件生成通知
class FilesCreationInformServerService(AbServerService):
    trade_no = '31101'
    msg_template = '<root>' \
                   '<pub>' \
                       '<InstructionCode>{InstructionCode}</InstructionCode>' \
                       '<Code>{Code></Code><Info>{Info}</Info>' \
                        '<Date>{Date}</Date><Time>{Time}</Time>' \
                        '<InstNo>{InstNo}</InstNo>' \
                   '</pub>' \
                    '<Serial><SerialNo>{SerialNo}</SerialNo><InstSerial>{InstSerial}</InstSerial></Serial>' \
                    '</root>'

    must_exist_item = {'InstructionCode',
                       'TradeSource',
                       'InstNo',
                       'Files',
                       }
    pass_exception_for_response = True

    def check_msg_text(self, data, pack_key, pin_key, mac_key):
        s = super(self.__class__, self).check_msg_text(data, pack_key, pin_key, mac_key)
        if s:
            return s

        m = {'InstructionCode': self.__class__.trade_no,  # 交易号
            'TradeSource': self.trade_source,   # 交易发起方
            'InstNo': self.get_mch_id(),   # 市场编号
            'Date': self.get_date(),
             'Time': self.get_time(),
             'InstSerial': self.create_ab_inst_serial(),   # 市场流水号
            'SerialNo': data.get('SerialNo', ''),
        }

        if m.get('Code'):
            t = self.make_data(m, pack_key, pin_key, mac_key)
            return t
        return None

    def do_work(self, data):
        # 充值，改变用户账户余额
        #
        # 记录日志  AbBankLog  id, 业务、发起方、状态、流水号，市场流水号、金额
        files = data['Files']

        file_names = str.split(files, '|') if files else []
        m = {
             'SerialNo': data.get('SerialNo', ''),
            'InstNo': data['InstNo'],
             'InstSerial': self.create_ab_inst_serial(),   # 市场流水号
             'TradeSource': self.trade_source,
             'Date': data.get('Date', ''),
             'Time': data.get('Time', ''),
            'file_names': file_names,
            'Code': '170000',
            'Info': '',
             }

        return m


    def do_work_2(self, data):
        # 充值，改变用户账户余额
        #
        # 记录日志  AbBankLog  id, 业务、发起方、状态、流水号，市场流水号、金额
        file_names = data.get('file_names', '')

        if file_names:
            received_file_names_done.send(sender=self.__class__, file_names=file_names, the_day=data['date'])

        return data
