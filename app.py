import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import folium_static
import plotly.express as px
import plotly.graph_objects as go
import time
from PIL import Image
import io
import base64
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler

# Yerel modülleri içe aktar
from data_fetcher import fetch_all_data, TURKEY_CITIES
from location_data import get_districts, get_neighborhoods, analyze_area, create_area_analysis_map
from utils import (
    create_map, plot_operator_distribution, plot_power_distribution, 
    plot_city_comparison, plot_demographic_data, calculate_location_score,
    create_roi_analysis, plot_roi_chart
)

# Sayfanın yapısını ayarla
st.set_page_config(
    page_title="Elektrikli Şarj İstasyonu Lokasyon Analizi",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS ile bazı stilleri ayarla
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #0277BD;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
        font-weight: bold;
    }
    .info-box {
        background-color: #E3F2FD;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        color: #333333;
    }
    .score-box {
        background-color: #E8F5E9;
        padding: 1.5rem;
        border-radius: 0.5rem;
        text-align: center;
        margin-bottom: 1rem;
        color: #333333;
    }
    .score-value {
        font-size: 3rem;
        font-weight: bold;
        color: #2E7D32;
    }
    .metric-container {
        display: flex;
        justify-content: space-between;
        flex-wrap: wrap;
    }
    .metric-box {
        background-color: #F5F5F5;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        text-align: center;
        width: 48%;
        color: #333333;
    }
    .roi-box {
        background-color: #FFF8E1;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        color: #333333;
    }
    .step-box {
        background-color: #F3E5F5;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        color: #333333;
    }
    .step-number {
        background-color: #9C27B0;
        color: white;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        margin-right: 10px;
        float: left;
    }
</style>
""", unsafe_allow_html=True)

# Başlık
st.markdown("<h1 class='main-header'>⚡ Elektrikli Şarj İstasyonu Lokasyon Analizi</h1>", unsafe_allow_html=True)

# Kenar çubuğu - Kullanıcı Tipi Seçimi
with st.sidebar:
    st.title("⚙️ Kontrol Paneli")
    
    # Kullanıcı tipi seçimi
    user_type = st.radio(
        "Kullanıcı Tipi",
        ("Genel Kullanıcı", "Yatırımcı"),
        index=0
    )
    
    st.divider()
    
    # Veri yükleme
    data = fetch_all_data()
    
    # Yatırımcı için analiz tipi seçimi
    if user_type == "Yatırımcı":
        analysis_type = st.radio(
            "Analiz Tipi",
            ("Konuma Göre Analiz", "Alana Göre Analiz"),
            index=0
        )
        
        st.divider()
        st.subheader("Yatırım Parametreleri")
        
        investment_amount = st.slider(
            "Yatırım Miktarı (TL)",
            min_value=50000,
            max_value=500000,
            value=150000,
            step=10000,
            format="%d TL"
        )
        
        charger_count = st.slider(
            "Şarj Noktası Sayısı",
            min_value=2,
            max_value=20,
            value=4
        )
        
        charger_power = st.select_slider(
            "Şarj Gücü (kW)",
            options=[50, 100, 150, 250, 350],
            value=150
        )
    else:
        # Genel kullanıcı için şehir seçimi
        cities = ["Tüm Şehirler"] + sorted(list(data["demographic_data"]["city"].unique()))
        selected_city = st.selectbox("Şehir Seçin", cities)
    
    st.divider()
    st.caption("© 2023 Elektrikli Şarj İstasyonu Analizi")
    st.caption("Endüstri Mühendisliği Bitirme Projesi")

# Ana sayfayı kullanıcı tipine göre yapılandır
if user_type == "Genel Kullanıcı":
    # Genel kullanıcı arayüzü
    tabs = st.tabs(["Şarj İstasyonu Haritası", "İstatistikler", "Demografik Analiz"])
    
    with tabs[0]:
        st.markdown("<h2 class='sub-header'>Türkiye Şarj İstasyonu Haritası</h2>", unsafe_allow_html=True)
        
        # Şarj istasyonu haritası
        charging_map = create_map(data["charging_stations"], selected_city)
        folium_static(charging_map, width=1000, height=500)
        
        # Bilgi kutusu
        st.markdown(
            "<div class='info-box'>"
            "Bu harita Türkiye'deki elektrikli araç şarj istasyonlarının dağılımını göstermektedir. "
            "Her bir marker bir şarj istasyonunu temsil eder. Üzerine tıklayarak detayları görebilirsiniz. "
            "Haritanın sağ üst köşesindeki katman kontrolü ile istasyonları operatöre göre filtreleyebilirsiniz."
            "</div>",
            unsafe_allow_html=True
        )
    
    with tabs[1]:
        st.markdown("<h2 class='sub-header'>Şarj İstasyonu İstatistikleri</h2>", unsafe_allow_html=True)
        
        # İstatistik grafikleri
        col1, col2 = st.columns(2)
        
        with col1:
            # Operatör dağılımı
            operator_fig = plot_operator_distribution(data["charging_stations"])
            st.plotly_chart(operator_fig, use_container_width=True)
            
            # Şehir karşılaştırması
            city_fig = plot_city_comparison(data["charging_stations"])
            st.plotly_chart(city_fig, use_container_width=True)
        
        with col2:
            # Güç dağılımı
            power_fig = plot_power_distribution(data["charging_stations"])
            st.plotly_chart(power_fig, use_container_width=True)
            
            # İstasyon yaş dağılımı
            year_counts = data["charging_stations"]["installation_year"].value_counts().sort_index()
            year_df = pd.DataFrame({
                "Yıl": year_counts.index,
                "İstasyon Sayısı": year_counts.values
            })
            year_fig = px.line(
                year_df,
                x="Yıl",
                y="İstasyon Sayısı",
                markers=True,
                title="Yıllara Göre Şarj İstasyonu Kurulum Sayıları",
                color_discrete_sequence=["#1E88E5"]
            )
            st.plotly_chart(year_fig, use_container_width=True)
    
    with tabs[2]:
        st.markdown("<h2 class='sub-header'>Demografik ve Trafik Analizi</h2>", unsafe_allow_html=True)
        
        # Demografik ısı haritası
        demo_fig = plot_demographic_data(data["demographic_data"], data["traffic_data"])
        st.plotly_chart(demo_fig, use_container_width=True)
        
        # Açıklama
        st.markdown(
            "<div class='info-box'>"
            "Bu ısı haritası, şehirlerin demografik ve trafik verilerini normalize edilmiş şekilde göstermektedir. "
            "Koyu renkler daha yüksek değerleri, açık renkler daha düşük değerleri temsil eder. "
            "Bu veriler, şarj istasyonu lokasyon seçiminde önemli faktörlerdir."
            "</div>",
            unsafe_allow_html=True
        )

else:  # Yatırımcı kullanıcı arayüzü
    if analysis_type == "Konuma Göre Analiz":
        st.markdown("<h2 class='sub-header'>Konum Bazlı Analiz</h2>", unsafe_allow_html=True)
        
        # Harita üzerinde konum seçimi
        st.markdown("Harita üzerinde analiz etmek istediğiniz konumu seçin:")
        
        # Harita
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Folium haritası oluştur
            m = create_map(data["charging_stations"], "Tüm Şehirler")
            m.add_child(folium.LatLngPopup())
            folium_static(m, width=800, height=500)
            
            # Konum girişi
            lat_lon_container = st.container()
            with lat_lon_container:
                col_lat, col_lon = st.columns(2)
                with col_lat:
                    latitude = st.number_input("Enlem", value=39.0, format="%.6f")
                with col_lon:
                    longitude = st.number_input("Boylam", value=35.0, format="%.6f")
        
        # Analiz butonu
        if st.button("Konumu Analiz Et", type="primary"):
            with st.spinner("Konum analizi yapılıyor..."):
                # Konum puanı hesapla
                location_score = calculate_location_score(
                    latitude, longitude, 
                    data["charging_stations"], 
                    data["demographic_data"], 
                    data["traffic_data"]
                )
                
                # Sonuçları göster
                col1, col2 = st.columns([3, 2])
                
                with col1:
                    st.markdown("<h3 class='sub-header'>Lokasyon Analiz Sonuçları</h3>", unsafe_allow_html=True)
                    
                    # Konum puanı
                    st.markdown(
                        f"<div class='score-box'>"
                        f"<div>Konum Uygunluk Puanı</div>"
                        f"<div class='score-value'>{location_score['score']}/100</div>"
                        f"<div>En yakın şehir: {location_score['nearest_city']}</div>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                    
                    # Demografik metrikler
                    st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
                    
                    metrics = [
                        {"label": "Nüfus", "value": f"{location_score['population']:,}"},
                        {"label": "Elektrikli Araç Benimseme Oranı", "value": f"%{location_score['ev_adoption_rate']*100:.1f}"},
                        {"label": "Ortalama Gelir", "value": f"₺{location_score['avg_income']:,}"},
                        {"label": "Günlük Trafik", "value": f"{location_score['traffic']:,}"},
                        {"label": "Yakındaki İstasyon Sayısı", "value": f"{location_score['nearest_stations']}"},
                        {"label": "Ortalama Mesafe", "value": f"{location_score['avg_distance_km']} km"}
                    ]
                    
                    for metric in metrics:
                        st.markdown(
                            f"<div class='metric-box'>"
                            f"<div>{metric['label']}</div>"
                            f"<div style='font-size: 1.5rem; font-weight: bold;'>{metric['value']}</div>"
                            f"</div>",
                            unsafe_allow_html=True
                        )
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                
                with col2:
                    st.markdown("<h3 class='sub-header'>Konum Değerlendirmesi</h3>", unsafe_allow_html=True)
                    
                    # Konum puanına göre değerlendirme
                    recommendation = ""
                    if location_score["score"] >= 80:
                        recommendation = "Bu konum şarj istasyonu kurulumu için **mükemmel** bir seçimdir. Yüksek potansiyel ve düşük rekabet barındırıyor."
                    elif location_score["score"] >= 60:
                        recommendation = "Bu konum şarj istasyonu kurulumu için **iyi** bir seçimdir. Yatırım için uygun koşullar mevcut."
                    elif location_score["score"] >= 40:
                        recommendation = "Bu konum şarj istasyonu kurulumu için **orta** düzeyde uygundur. Bazı risk faktörleri mevcut olabilir."
                    else:
                        recommendation = "Bu konum şarj istasyonu kurulumu için **düşük** uygunluktadır. Alternatif lokasyonlar değerlendirilmelidir."
                    
                    st.markdown(f"<div class='info-box'>{recommendation}</div>", unsafe_allow_html=True)
                    
                    # Öneriler
                    st.markdown("<h4>Öneriler</h4>", unsafe_allow_html=True)
                    suggestions = []
                    
                    if location_score["nearest_stations"] > 3:
                        suggestions.append("Bu bölgede rekabet yüksek olabilir. Farklılaşmak için daha yüksek güçlü şarj cihazları düşünebilirsiniz.")
                    
                    if location_score["ev_adoption_rate"] < 0.05:
                        suggestions.append("Bölgedeki elektrikli araç benimseme oranı düşük. Uzun vadeli bir yatırım stratejisi düşünülmelidir.")
                    
                    if location_score["avg_distance_km"] > 5:
                        suggestions.append("En yakın rakiplere mesafe yeterli. Bu, müşteri çekmek için bir avantaj olabilir.")
                    
                    if location_score["traffic"] > 500000:
                        suggestions.append("Bölgedeki trafik yoğunluğu yüksek. Bu, potansiyel müşteri hacmi için olumludur.")
                    
                    if not suggestions:
                        suggestions.append("Lokasyon genel olarak uygun görünüyor. Standart kurulum planınızla ilerleyebilirsiniz.")
                    
                    for suggestion in suggestions:
                        st.markdown(f"- {suggestion}")
    
    else:  # Alana Göre Analiz
        st.markdown("<h2 class='sub-header'>Alan Bazlı Analiz</h2>", unsafe_allow_html=True)
        
        # Bölge seçimi
        col1, col2, col3 = st.columns(3)
        
        with col1:
            selected_city = st.selectbox(
                "İl Seçin",
                sorted(TURKEY_CITIES),
                index=TURKEY_CITIES.index("İstanbul")
            )
        
        with col2:
            # Seçilen ile göre ilçeleri getir
            districts = get_districts(selected_city)  # Bu fonksiyon oluşturulacak
            selected_district = st.selectbox("İlçe Seçin", ["Tüm İlçeler"] + districts)
        
        with col3:
            if selected_district != "Tüm İlçeler":
                # Seçilen ilçeye göre mahalleleri getir
                neighborhoods = get_neighborhoods(selected_city, selected_district)  # Bu fonksiyon oluşturulacak
                selected_neighborhood = st.selectbox("Mahalle Seçin (Opsiyonel)", ["Tüm Mahalleler"] + neighborhoods)
        
        # Analiz butonu
        if st.button("Bölgeyi Analiz Et", type="primary"):
            with st.spinner("Bölge analizi yapılıyor..."):
                # Seçilen bölgeye göre potansiyel lokasyonları belirle
                potential_locations = analyze_area(
                    selected_city,
                    selected_district,
                    selected_neighborhood if 'selected_neighborhood' in locals() else None
                )
                
                # Harita üzerinde potansiyel lokasyonları göster
                st.markdown("<h3 class='sub-header'>Potansiyel Şarj İstasyonu Lokasyonları</h3>", unsafe_allow_html=True)
                
                area_map = create_area_analysis_map(
                    potential_locations,
                    selected_city,
                    selected_district,
                    selected_neighborhood if 'selected_neighborhood' in locals() else None
                )
                folium_static(area_map, width=1000, height=500)
                
                # Potansiyel lokasyonların detaylı analizi
                st.markdown("<h3 class='sub-header'>Lokasyon Değerlendirmeleri</h3>", unsafe_allow_html=True)
                
                for idx, location in enumerate(potential_locations, 1):
                    with st.expander(f"Lokasyon {idx} - Puan: {location['score']}/100"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"**Konum:** {location['address']}")
                            st.markdown(f"**Koordinatlar:** {location['lat']}, {location['lon']}")
                            st.markdown(f"**Tahmini Günlük Trafik:** {location['daily_traffic']:,}")
                            st.markdown(f"**Yakındaki İşletme Sayısı:** {location['nearby_businesses']}")
                        
                        with col2:
                            st.markdown(f"**Rekabet Durumu:** {location['competition_level']}")
                            st.markdown(f"**Tahmini Aylık Gelir:** ₺{location['estimated_revenue']:,}")
                            st.markdown(f"**Geri Dönüş Süresi:** {location['roi_months']:.1f} ay")
                            st.markdown(f"**Risk Seviyesi:** {location['risk_level']}")
                
                # Bölge özeti
                st.markdown("<h3 class='sub-header'>Bölge Özeti</h3>", unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(
                        "<div class='info-box'>"
                        f"<b>Toplam Potansiyel Lokasyon:</b> {len(potential_locations)}<br>"
                        f"<b>Ortalama Lokasyon Puanı:</b> {sum(loc['score'] for loc in potential_locations)/len(potential_locations):.1f}/100<br>"
                        f"<b>En İyi Lokasyon Puanı:</b> {max(loc['score'] for loc in potential_locations)}/100<br>"
                        f"<b>Mevcut İstasyon Sayısı:</b> {len(data['charging_stations'][data['charging_stations']['city'] == selected_city])}"
                        "</div>",
                        unsafe_allow_html=True
                    )
                
                with col2:
                    st.markdown(
                        "<div class='info-box'>"
                        f"<b>Bölge Nüfusu:</b> {data['demographic_data'][data['demographic_data']['city'] == selected_city]['population'].iloc[0]:,}<br>"
                        f"<b>Elektrikli Araç Oranı:</b> {data['demographic_data'][data['demographic_data']['city'] == selected_city]['ev_adoption_rate'].iloc[0]*100:.1f}%<br>"
                        f"<b>Trafik Yoğunluğu:</b> {data['traffic_data'][data['traffic_data']['city'] == selected_city]['congestion_index'].iloc[0]}/10<br>"
                        f"<b>Büyüme Potansiyeli:</b> {data['demographic_data'][data['demographic_data']['city'] == selected_city]['growth_potential'].iloc[0]*100:.1f}%"
                        "</div>",
                        unsafe_allow_html=True
                    )

if __name__ == "__main__":
    pass 
