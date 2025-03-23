from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from django.utils.dateformat import DateFormat
import datetime


class JazzCashPayment(APIView):
    # authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        user = 'jamshaid iqbal'
        date_time = datetime.datetime.now()
        tran_time = datetime.datetime.now() + datetime.timedelta(days=8)
        tran_time = DateFormat(tran_time)
        tran_time = str(tran_time.format('YmdHis'))
        pp_TranExpiryDateTime = tran_time
        date_time = DateFormat(date_time)
        date_time = str(date_time.format('YmdHis'))
        pp_TxnDateTime = date_time
        pp_TxnRefNo = "T" + date_time
        pp_BillReference = str('13546khacajchxskhdk')
        salt = str(settings.JAZZCASH_SALT)
        payment_info_dict = {'pp_Version': '1.1', 'pp_TxnType': '', 'pp_Language': 'EN',
                             'pp_MerchantID': str(settings.JAZZCASH_MERCHAT_ID),
                             'pp_SubMerchantID': '', 'pp_Password': str(settings.JAZZCASH_PASSWORD),
                             'pp_BankID': 'TBANK',
                             'pp_ProductID': 'RETL', 'pp_TxnRefNo': pp_TxnRefNo,
                             'pp_Amount': str(int(1) * 100),
                             'pp_TxnCurrency': "PKR", 'pp_TxnDateTime': pp_TxnDateTime,
                             'pp_BillReference': pp_BillReference,
                             'pp_Description': '{user} is paying for section'.format(user=user),
                             'pp_TxnExpiryDateTime': pp_TranExpiryDateTime,
                             'pp_ReturnURL': '/',
                             'pp_SecureHash': '2da1823dc796b923bf1998345087829695a533890362547fe6fab7d24f3e2c45',
                             'ppmpf_1': '1',
                             'ppmpf_2': '2',
                             'ppmpf_3': '3',
                             'ppmpf_4': '4',
                             'ppmpf_5': '5',
                             'pp_TranExpiryDateTime': pp_TranExpiryDateTime,
                             'HMAC_URL': settings.JAZZCASH_HMAC_URL,
                             'POST_URL': settings.JAZZCASH_POST_URL,
                             'salt': salt
                             }
        query_string = "&".join([
            payment_info_dict.get('salt'),
            payment_info_dict.get('pp_Amount'),
            payment_info_dict.get('pp_BankID'),
            payment_info_dict.get('pp_BillReference'),
            payment_info_dict.get('pp_Description'),
            payment_info_dict.get('pp_Language'),
            payment_info_dict.get('pp_MerchantID'),
            payment_info_dict.get('pp_Password'),
            payment_info_dict.get('pp_ProductID'),
            payment_info_dict.get('pp_ReturnURL'),
            payment_info_dict.get('pp_SubMerchantID'),
            payment_info_dict.get('pp_TxnCurrency'),
            payment_info_dict.get('pp_TxnDateTime'),
            payment_info_dict.get('pp_TxnExpiryDateTime'),
            payment_info_dict.get('pp_TxnRefNo'),
            payment_info_dict.get('pp_TxnType'),
            payment_info_dict.get('pp_Version'),
            payment_info_dict.get('ppmpf_1'),
            payment_info_dict.get('ppmpf_2'),
            payment_info_dict.get('ppmpf_3'),
            payment_info_dict.get('ppmpf_4'),
            payment_info_dict.get('ppmpf_5')
        ])
        payment_info_dict['query_string'] = query_string
        return Response(payment_info_dict)
