
from django import forms


CITY_CHOICES = [
    ('Ahmedabad', 'Ahmedabad'),
    ('Chennai', 'Chennai'),
    ('Dahej', 'Dahej'),
    ('Faridabad', 'Faridabad'),
    ('Gurgaon', 'Gurgaon'),
    ('Hyderabad', 'Hyderabad'),
    ('Kolkata', 'Kolkata'),
    ('Mumbai', 'Mumbai'),
    ('Nagpur', 'Nagpur'),
    ('Navi Mumbai', 'Navi Mumbai'),
    ('New Delhi', 'New Delhi'),
    ('Noida', 'Noida'),
    ('Pune', 'Pune'),
    ('Ratnagiri', 'Ratnagiri'),
    ('Shimla', 'Shimla'),
    ('Vadodara', 'Vadodara'),
]

COMPANY_CHOICES = [
    ('Adani Power Ltd.', 'Adani Power Ltd.'),
    ('Bonfiglioli Transmission Pvt. Ltd.', 'Bonfiglioli Transmission Pvt. Ltd.'),
    ('CESC', 'CESC'),
    ('GE T&D India Limited', 'GE T&D India Limited'),
    ('Guj Ind Power', 'Guj Ind Power'),
    ('Indowind Energy', 'Indowind Energy'),
    ('JSW Energy Ltd.', 'JSW Energy Ltd.'),
    ('Jaiprakash Power', 'Jaiprakash Power'),
    ('Jyoti Structure', 'Jyoti Structure'),
    ('KEC International', 'KEC International'),
    ('Kalpataru Power', 'Kalpataru Power'),
    ('L&T Transmission & Distribution', 'L&T Transmission & Distribution'),
    ('Maha Transco – Maharashtra State Electricity Transmission Co, Ltd.', 'Maha Transco'),
    ('NHPC', 'NHPC'),
    ('NLC India', 'NLC India'),
    ('NTPC Pvt. Ltd.', 'NTPC Pvt. Ltd.'),
    ('Neueon Towers / Sujana Towers Ltd.', 'Neueon Towers / Sujana Towers Ltd.'),
    ('Optibelt Power Transmission India Private Limited', 'Optibelt Power Transmission India Private Limited'),
    ('Orient Green', 'Orient Green'),
    ('Power Grid Corp', 'Power Grid Corp'),
    ('Ratnagiri Gas and Power Pvt. Ltd. (RGPPL)', 'Ratnagiri Gas and Power Pvt. Ltd.'),
    ('Reliance Energy', 'Reliance Energy'),
    ('Reliance Power', 'Reliance Power'),
    ('Ringfeder Power Transmission India Pvt. Ltd.', 'Ringfeder Power Transmission India Pvt. Ltd.'),
    ('SJVN Ltd.', 'SJVN Ltd.'),
    ('Sterlite Power Transmission Ltd', 'Sterlite Power Transmission Ltd'),
    ('Sunil Hitech Eng', 'Sunil Hitech Eng'),
    ('Tata Power Company Ltd.', 'Tata Power Company Ltd.'),
    ('Torrent Power Ltd.', 'Torrent Power Ltd.'),
    ('Toshiba Transmission & Distribution Systems (India) Pvt. Ltd.', 'Toshiba Transmission & Distribution Systems (India) Pvt. Ltd.'),
    ('TransRail Lighting', 'TransRail Lighting'),
    ('Unitech Power Transmission Ltd.', 'Unitech Power Transmission Ltd.'),
]


class PrediksiForm(forms.Form):
    fan = forms.IntegerField(
        label='Jumlah Kipas',
        min_value=5,
        max_value=23,
        initial=14,
    )

    refrigerator = forms.IntegerField(
        label='Jumlah Kulkas',
        min_value=17,
        max_value=23,
        initial=22,
    )

    air_conditioner = forms.IntegerField(
        label='Jumlah AC',
        min_value=0,
        max_value=3,
        initial=2,
    )

    television = forms.IntegerField(
        label='Jumlah Televisi',
        min_value=3,
        max_value=22,
        initial=13,
    )

    monitor = forms.IntegerField(
        label='Jumlah Monitor',
        min_value=1,
        max_value=12,
        initial=1,
    )

    month = forms.TypedChoiceField(
        label='Bulan',
        choices=[(i, f'Bulan {i}') for i in range(1, 13)],
        coerce=int,
        initial=1,
    )

    city = forms.ChoiceField(
        label='Kota',
        choices=CITY_CHOICES,
    )

    company = forms.ChoiceField(
        label='Perusahaan',
        choices=COMPANY_CHOICES,
    )

    monthly_hours = forms.FloatField(
        label='Total Jam Penggunaan Bulanan',
        min_value=95,
        max_value=926,
        initial=515,
    )

    tariff_rate = forms.FloatField(
        label='Tarif Listrik',
        min_value=7.4,
        max_value=9.3,
        initial=8.4,
        widget=forms.NumberInput(attrs={'step': '0.1'}),
    )
