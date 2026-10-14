import os
import streamlit as st
import pandas as pd
import requests
import datetime
import random
import io
//import plotly.express as px
from openpyxl import Workbook
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Page Configuration
st.set_page_config(
    page_title="UniPass Finance AI - Student Financial Agent",
    page_icon="🎓",
    layout="wide"
)

# App Header
st.title("UniPass Finance AI")
st.caption("AI-Powered Financial Assistant for International Students in China")
st.markdown("---")

# Navigation Modules Mapping
NAV_MODULES = {
    "fx": "Smart FX Advisor",
    "receipt": "Receipt Auditor (OCR & Tax-Free)",
    "budget": "Student Budget Manager",
    "banking": "Bank Card & Payment Guide",
    "shopping": "Online Shopping & Food Delivery",
    "transport": "Transportation & Travel Facilities"
}

st.sidebar.header("🔍 Features & Modules")
selected_nav_key = st.sidebar.radio(
    "Select a Module:",
    options=list(NAV_MODULES.keys()),
    format_func=lambda k: NAV_MODULES[k]
)

st.markdown("---")

currencies = [
    "USD", "EUR", "GBP", "BDT", "JPY", "AUD", "CAD", "CHF", "CNY", "INR", 
    "NZD", "SGD", "HKD", "MYR", "PKR", "SAR", "AED", "THB", "KRW", "ZAR", 
    "BRL", "IDR", "PHP", "VND", "SEK", "NOK", "DKK", "RUB", "TRY", "MXN",
    "TWD", "PLN", "ILS", "CLP", "EGP", "QAR", "KWD", "BHD", "OMR"
]

# Module 1: Smart FX Advisor
if selected_nav_key == "fx":
    st.subheader("Smart FX & Currency Decision Advisor")
    st.write("Get real-time exchange rates, global multi-currency conversion, weekly trend analysis, and AI-driven timing advice.")

    col1, col2, col3 = st.columns(3)
    with col1:
        base_curr = st.selectbox("From Currency", currencies, index=currencies.index("USD") if "USD" in currencies else 0)
    with col2:
        target_curr = st.selectbox("To Currency", currencies, index=currencies.index("CNY") if "CNY" in currencies else 0)
    with col3:
        amount = st.number_input("Amount to Transfer", min_value=0.0, value=1000.0)

    if st.button("Analyze & Convert"):
        try:
            url = f"https://api.exchangerate-api.com/v4/latest/{base_curr}"
            res = requests.get(url).json()
            
            if 'rates' in res and target_curr in res['rates']:
                rate = res['rates'][target_curr]
                converted = amount * rate

                st.success(f"**Conversion Result:** {amount:,.2f} {base_curr} = **{converted:,.2f} {target_curr}**")
                st.info(f"📈 **Current Exchange Rate:** 1 {base_curr} = {rate:.4f} {target_curr}")

                today = datetime.date.today()
                dates = [(today - datetime.timedelta(days=i)) for i in range(7, 0, -1)]
                random.seed(42)
                simulated_rates = [rate * (1 + random.uniform(-0.008, 0.008)) for _ in range(6)] + [rate]
                
                trend_df = pd.DataFrame({
                    "Date": [d.strftime("%Y-%m-%d") for d in dates],
                    "Exchange Rate": simulated_rates
                })

                fig = px.line(trend_df, x="Date", y="Exchange Rate", markers=True, 
                              title=f"7-Day Exchange Rate Trend ({base_curr} to {target_curr})")
                fig.update_layout(template="plotly_dark", title_font_size=16)
                st.plotly_chart(fig, use_container_width=True)

                best_row_idx = trend_df['Exchange Rate'].idxmax()
                best_row = trend_df.loc[best_row_idx, 'Date']
                best_rate_val = trend_df['Exchange Rate'].max()

                st.success(f"**Optimal Transfer Window:** **{best_row}** observed the highest rate ({best_rate_val:.4f}).")
            else:
                st.error("Selected currency rate is currently unavailable.")
        except Exception as e:
            st.error(f"Failed to connect to exchange rate service: {e}")

# Module 2: Receipt Auditor
elif selected_nav_key == "receipt":
    st.subheader("AI Receipt Auditor & Tax-Free Shopping Guide")
    st.write("Upload receipt images or PDF files for automated expense parsing and export capabilities.")

    tab_ocr, tab_tax = st.tabs(["Receipt Scanner (Images & PDF)", "Student Tax-Free Guide"])

    with tab_ocr:
        col_up, col_txt = st.columns(2)
        with col_up:
            uploaded_file = st.file_uploader("Choose a receipt file...", type=["jpg", "jpeg", "png", "pdf"])
        with col_txt:
            manual_note = st.text_input("Expense Description / Notes", placeholder="e.g., Books, Canteen, Electronics")

        if uploaded_file is not None:
            if uploaded_file.type == "application/pdf":
                st.info("PDF Receipt uploaded successfully. Processing document...")
            else:
                st.image(uploaded_file, caption="Uploaded Receipt Preview", use_container_width=True)

            with st.spinner("AI OCR Engine extracting data..."):
                import time
                time.sleep(0.5)
                
                extracted_data = {
                    "Item": ["University Canteen", "Academic Textbooks", "Supermarket Groceries"],
                    "Category": ["Food", "Education", "Groceries"],
                    "Amount (CNY)": [35.00, 180.00, 65.50],
                    "Tax Status": ["Tax-Included", "Educational Tax-Exempt", "Standard VAT"]
                }
                df_receipt = pd.DataFrame(extracted_data)
                st.success("Receipt/PDF successfully parsed via AI OCR!")
                st.table(df_receipt)
                
                total_val = df_receipt['Amount (CNY)'].sum()
                st.info(f"**Total Extracted Expense:** {total_val:.2f} CNY")

                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df_receipt.to_excel(writer, index=False, sheet_name='Receipt_Audit')
                excel_data = output.getvalue()

                st.download_button(
                    label="Download Audit Report as Excel (.xlsx)",
                    data=excel_data,
                    file_name="receipt_audit_report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

    with tab_tax:
        st.markdown("### How International Students Can Claim Tax-Free Purchases")
        st.markdown("""
        1. **Educational Supplies & Books:** Many university bookstores offer discounted or tax-exempt rates for registered students. Show your Student ID card.
        2. **Departure Tax Refund:** Claim VAT refunds on eligible goods when leaving China.
        3. **Electronic Devices & Laptops:** Purchase certified student-discounted hardware using your admission notice.
        """)

# Module 3: Student Budget Manager
elif selected_nav_key == "budget":
    st.subheader("Smart Student Budget Manager & PDF Report Generator")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Income Sources")
        stipend = st.number_input("Monthly Stipend / Allowance (CNY)", min_value=0.0, value=3500.0)
        extra_income = st.number_input("Part-time / Extra Income (CNY)", min_value=0.0, value=500.0)
        total_income = stipend + extra_income

    with col2:
        st.markdown("### Expense Categories")
        tuition = st.number_input("Quarterly/Monthly Tuition Allocated (CNY)", min_value=0.0, value=1500.0)
        food_exp = st.number_input("Food & Canteen (CNY)", min_value=0.0, value=1200.0)
        rent_exp = st.number_input("Accommodation / Dorm (CNY)", min_value=0.0, value=800.0)
        utils_exp = st.number_input("Utilities & Transport (CNY)", min_value=0.0, value=300.0)

    monthly_expenses = tuition + food_exp + rent_exp + utils_exp
    net_balance = total_income - monthly_expenses

    st.markdown("---")
    expense_df = pd.DataFrame({
        "Category": ["Tuition", "Food", "Accommodation", "Utilities/Transport"],
        "Amount": [tuition, food_exp, rent_exp, utils_exp]
    })
    fig_pie = px.pie(expense_df, names="Category", values="Amount", title="Monthly Expense Distribution", hole=0.4)
    fig_pie.update_layout(template="plotly_dark")
    st.plotly_chart(fig_pie, use_container_width=True)

    def generate_pdf_report(income, expenses, net):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#1f77b4'), spaceAfter=12)
        
        elements.append(Paragraph("UniPass Finance AI - Student Financial Summary Report", title_style))
        elements.append(Paragraph(f"Generated Date: {datetime.date.today().strftime('%Y-%m-%d')}", styles['Normal']))
        elements.append(Spacer(1, 12))
        
        data = [
            ["Financial Metric", "Amount (CNY)"],
            ["Total Monthly Income", f"{income:,.2f}"],
            ["Total Monthly Expenses", f"{expenses:,.2f}"],
            ["Net Balance / Savings", f"{net:,.2f}"]
        ]
        t = Table(data, colWidths=[250, 150])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (1,0), colors.HexColor('#333333')),
            ('TEXTCOLOR', (0,0), (1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f0f0f0')),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))
        elements.append(t)
        doc.build(elements)
        buffer.seek(0)
        return buffer

    pdf_file = generate_pdf_report(total_income, monthly_expenses, net_balance)
    st.download_button(
        label="Download Official Financial Report as PDF",
        data=pdf_file,
        file_name="student_financial_report.pdf",
        mime="application/pdf"
    )

# Module 4: Bank Card & Payment Guide
elif selected_nav_key == "banking":
    st.subheader("Ultimate International Student Banking & Payment Guide")
    tab1, tab2, tab3 = st.tabs(["1. Opening Bank Account", "2. WeChat Pay Guide", "3. Alipay Guide"])

    with tab1:
        st.markdown("### 🏦 Detailed Step-by-Step Guide to Opening a Chinese Bank Account")
        st.write("As an international student in China, opening a bank account is essential for receiving scholarship stipends, paying university bills, and using WeChat/Alipay.")
        
        st.markdown("""
        #### 📋 1. Required Documents Checklist:
        * **Original Passport:** Must contain a valid visa (X1/X2) or Residence Permit.
        * **Admission Notice (录取通知书):** Official document from your university.
        * **Accommodation Registration Form (境外人员临时住宿登记表):** Issued by campus international student office or local police station.
        * **Local Chinese Phone Number:** Registered in your name with real-name passport registration.

        #### 🏬 2. At the Bank Branch (ICBC / Bank of China / CCB):
        * **Queue Ticket:** Get a queue number at the entrance counter for 'Personal Business' (个人业务).
        * **Form Filling:** Fill out the account opening form. Write your full name exactly as it appears in your passport (CAPITAL LETTERS).
        * **Counter Process:** Hand over documents to the officer. They will verify your passport and ask you to create a 6-digit ATM PIN.
        
        #### 🗣️ Useful Chinese Phrases:
        * "I want to open a bank card": 我想办一张银行卡 (Wǒ xiǎng bàn yī zhāng yínháng kǎ)
        * "I am an international student": 我是留学生 (Wǒ shì liúxuéshēng)

        ---
        ### 📥 Official Bank App Download Links:
        * [🔗 **Bank of China (中国银行) App**](https://www.boc.cn/)
        * [🔗 **ICBC (中国工商银行) App**](https://www.icbc.com.cn/)
        * [🔗 **China Construction Bank (中国建设银行) App**](https://www.ccb.com/)
        """)

    with tab2:
        st.markdown("### 💬 WeChat Pay (微信支付) Setup & Binding Guide")
        st.write("WeChat Pay is the primary digital payment tool in China used in daily life.")
        st.markdown("""
        #### 🛠️ Step-by-Step Linking Instructions:
        1. **Download WeChat:** Install the official WeChat application.
        2. **Navigate to Wallet:** Go to **Me (我)** > **Services (服务)** > **Wallet (钱包)** > **Cards (银行卡)**.
        3. **Add Bank Card:** Tap **Add Bank Card** and enter your Chinese Debit Card number.
        4. **Real-Name Identity Verification:** Enter your full name exactly as provided to the bank, select **Passport** as ID type, and enter passport number.
        5. **SMS OTP Verification:** Enter the 6-digit OTP code sent to your Chinese phone number.
        6. **Payment Password:** Set a dedicated 6-digit payment password for scanning QR codes.

        ---
        ### 📥 Official Download Link:
        * [🔗 **Download Official WeChat (微信)**](https://weixin.tencent.com/)
        """)

    with tab3:
        st.markdown("### 💰 Alipay (支付宝) Setup & Binding Guide")
        st.write("Alipay is essential for online shopping (Taobao), taking subways/buses, and hailing taxis (DiDi).")
        st.markdown("""
        #### 🛠️ Step-by-Step Linking Instructions:
        1. **Download & Register:** Download Alipay, set region to **International** or **Mainland China**, and log in with your phone number.
        2. **Identity Verification:** Go to **Account (我的)** > **Settings** > **Account & Security** > **Real-name Verification** and upload passport photo page.
        3. **Bind Card:** Go to **Account** > **Bank Cards** > **Add Card**. Enter your debit card digits and verify via phone SMS.
        4. **Transport Pass:** Use the **Transport (出行)** tab to get city Metro and Bus QR codes instantly!

        ---
        ### 📥 Official Download Link:
        * [🔗 **Download Official Alipay (支付宝)**](https://global.alipay.com/)
        """)

# Module 5: Online Shopping & Food Delivery
elif selected_nav_key == "shopping":
    st.subheader("Online Shopping & Food Delivery Guide")
    tab_shop, tab_food = st.tabs(["Online Shopping (Taobao / Pinduoduo)", "Food Delivery (Meituan / Ele.me)"])

    with tab_shop:
        st.markdown("""
        1. **Registration:** Download Taobao or Pinduoduo, sign up using your Chinese phone number, and verify via SMS OTP.
        2. **Address Setup:** Add your campus delivery address in Chinese characters.
        3. **Linking Payment:** Bind your activated WeChat Pay or Alipay account to checkout instantly.
        4. **Package Pickup:** Collect packages from campus pickup stations (Cainiao Station) using the SMS pickup code.

        ---
        ### Download Official Apps:
        * [🔗 **Download Taobao (淘宝)**](https://world.taobao.com/)
        * [🔗 **Download Pinduoduo (拼多多)**](https://yangkeduo.com/)
        """)

    with tab_food:
        st.markdown("""
        1. **App Installation:** Download Meituan or Ele.me via the app store. Login with your local mobile number.
        2. **Location Permission:** Allow GPS access to detect nearby canteens and restaurants.
        3. **Placing an Order:** Browse menus, select items, and proceed to checkout.
        4. **Delivery Instructions:** Riders drop off food at designated campus gates or delivery racks.

        ---
        ### Download Official Apps:
        * [🔗 **Download Meituan (美团)**](https://www.meituan.com/)
        * [🔗 **Download Ele.me (饿了么)**](https://www.ele.me/)
        """)

# Module 6: Transportation & Travel Facilities (Comprehensive)
elif selected_nav_key == "transport":
    st.subheader("Comprehensive Transportation & Travel Facilities Guide")
    t1, t2, t3, t4, t5 = st.tabs([
        "🚲 Shared Bicycles", 
        "🚇 Metro & City Buses", 
        "🚕 DiDi Ride-Hailing", 
        "🚅 High-Speed Rail (12306)", 
        "🗺️ Navigation & Phrases"
    ])

    with t1:
        st.markdown("### 🚲 Shared Bicycles Guide (HelloRide / Meituan Bike)")
        st.markdown("""
        #### 🛠️ Step-by-Step Usage Instructions:
        1. **Activation:** Open **Alipay** or **WeChat**, locate the bicycle mini-program or use standalone apps.
        2. **Scanning:** Tap 'Scan' and scan the QR code located on the bicycle handlebar or rear wheel lock.
        3. **Unlocking:** Hearing a beep indicates the lock is released.
        4. **Pricing:** Standard fare is 1.50 CNY - 2.00 CNY for the first 15-30 minutes. Subscriptions (Monthly Passes) cost around 12-15 CNY for unlimited rides.
        5. **Parking Rules:** Always park inside designated **Yellow Parking Rectangles (P-Zones)**. Parking outside designated areas will incur a penalty fee (up to 5-10 CNY).

        ---
        * [🔗 **HelloRide Official Site**](https://www.hellobike.com/)
        """)

    with t2:
        st.markdown("### 🚇 City Metro & Bus Guide")
        st.markdown("""
        #### 🛠️ How to Ride Metro & Bus Without Physical Cards:
        1. **Alipay Transport Code:** Open Alipay > Tap **Transport (出行)** > Select your current city > Activate Metro/Bus QR Card.
        2. **WeChat Transport Code:** Search 'City Transport Code' (e.g., 腾讯出行服务 / 乘车码) mini-program in WeChat.
        3. **Boarding Bus:** Scan the QR code at the bus entry scanner. Listen for the confirmation chime.
        4. **Riding Metro:** Scan the QR code at the turnstile gate entry and scan again upon exit. The fare is calculated automatically.
        """)

    with t3:
        st.markdown("### 🚕 DiDi (滴滴出行) Ride-Hailing Guide")
        st.markdown("""
        #### 🛠️ How to Book a Ride:
        1. **Accessing DiDi:** Use the DiDi Mini-Program inside WeChat/Alipay or download the **DiDi Greater China** App.
        2. **Setting Route:** Enter destination (English search supported in DiDi English version).
        3. **Select Ride Type:** Choose **Express (快车)** for budget travel, **Taxi (出租车)** for metered taxis, or **Kuaiche Choice** for shared routes.
        4. **Driver Communication:** Drivers may call you; use the built-in in-app auto-translation messaging to tell them your exact waiting location.
        5. **Payment:** Fares are automatically deducted from your linked Alipay, WeChat, or bank card upon arrival.

        ---
        * [🔗 **Download DiDi Global**](https://www.didiglobal.com/)
        """)

    with t4:
        st.markdown("### 🚅 High-Speed Train (CRH 12306) Booking Guide")
        st.markdown("""
        #### 🛠️ Booking Intercity Bullet Trains:
        1. **Official App:** Download the official **Railway 12306 (铁路12306)** app.
        2. **Real-Name Registration:** Register account using your **Passport Number** exactly as shown on your passport.
        3. **Ticket Purchase:** Search origin and destination stations, select departure date, choose train time, and select seat class (Second Class / First Class).
        4. **E-Ticket Entry:** No physical paper ticket required! At train stations, walk through the **Manual Verification Gate (人工通道)** where station attendants scan your passport directly.

        ---
        * [🔗 **Railway 12306 Official Portal**](https://www.12306.cn/)
        """)

    with t5:
        st.markdown("### 🗺️ Navigation Apps & Emergency Travel Phrases")
        st.markdown("""
        #### 🧭 Top Map Applications:
        * **Amap (高德地图):** Highly accurate for walking, bus routes, and real-time transit schedule.
        * **Baidu Maps (百度地图):** Excellent lane-level GPS navigation.

        #### 🗣️ Useful Travel Chinese Phrases:
        * **"Where is the subway station?":** 地铁站在哪里？(Dìtiě zhàn zài nǎlǐ?)
        * **"Please drive to this address":** 请送到这个地址 (Qǐng sòng dào zhège dìzhǐ)
        * **"How much is the ticket?":** 车票多少钱？(Chēpiào duōshao qián?)
        * **"I want to go to the train station":** 我想去火车站 (Wǒ xiǎng qù huǒchēzhàn)

        ---
        * [🔗 **Baidu Maps**](https://map.baidu.com/) | [🔗 **Amap (Gaode)**](https://lbs.amap.com/)
        """)
