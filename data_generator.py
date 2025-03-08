import pandas as pd
import numpy as np
import random

def generate_cities():
    """Türkiye'nin büyük şehirlerini ve koordinatlarını içeren veri seti."""
    cities = {
        "İstanbul": {"lat": 41.0082, "lon": 28.9784, "population": 15462000},
        "Ankara": {"lat": 39.9334, "lon": 32.8597, "population": 5639000},
        "İzmir": {"lat": 38.4237, "lon": 27.1428, "population": 4367000},
        "Bursa": {"lat": 40.1885, "lon": 29.0610, "population": 3056000},
        "Antalya": {"lat": 36.8969, "lon": 30.7133, "population": 2511000},
        "Adana": {"lat": 37.0000, "lon": 35.3213, "population": 2237000},
        "Konya": {"lat": 37.8719, "lon": 32.4844, "population": 2232000},
        "Gaziantep": {"lat": 37.0662, "lon": 37.3833, "population": 2069000},
        "Şanlıurfa": {"lat": 37.1591, "lon": 38.7969, "population": 2073000},
        "Mersin": {"lat": 36.8000, "lon": 34.6333, "population": 1840000},
        "Diyarbakır": {"lat": 37.9144, "lon": 40.2306, "population": 1756000},
        "Kayseri": {"lat": 38.7312, "lon": 35.4787, "population": 1400000},
        "Eskişehir": {"lat": 39.7767, "lon": 30.5206, "population": 871000},
        "Samsun": {"lat": 41.2867, "lon": 36.3300, "population": 1335000},
        "Denizli": {"lat": 37.7765, "lon": 29.0864, "population": 1033000},
    }
    
    return cities

def generate_charging_stations(cities, num_stations=200):
    """Rastgele şarj istasyonları oluşturur."""
    stations = []
    station_id = 1
    
    for city_name, city_data in cities.items():
        # Büyük şehirlere daha fazla istasyon atanır (nüfusa göre)
        city_stations = int(num_stations * (city_data["population"] / 15462000) * 0.7) + 2
        
        for _ in range(city_stations):
            # Şehir merkezi etrafında rastgele konumlar
            lat_offset = np.random.normal(0, 0.05)
            lon_offset = np.random.normal(0, 0.05)
            
            station = {
                "station_id": station_id,
                "name": f"{city_name} Şarj İstasyonu {station_id}",
                "city": city_name,
                "latitude": city_data["lat"] + lat_offset,
                "longitude": city_data["lon"] + lon_offset,
                "charger_count": random.randint(2, 12),
                "power_kw": random.choice([50, 100, 150, 250, 350]),
                "avg_daily_usage": random.randint(5, 40),
                "operator": random.choice(["ZES", "Eşarj", "Sharz", "Voltrun", "Epoint", "Elektrikli"]),
                "installation_year": random.randint(2018, 2023),
                "installation_cost": random.randint(20000, 150000),
                "monthly_revenue": random.randint(5000, 40000),
                "operational_cost": random.randint(2000, 15000),
                "customer_rating": round(random.uniform(3.0, 5.0), 1)
            }
            
            stations.append(station)
            station_id += 1
    
    return pd.DataFrame(stations)

def generate_demographic_data(cities):
    """Şehirler için demografik veri oluşturur."""
    demographic_data = []
    
    for city_name, city_data in cities.items():
        data = {
            "city": city_name,
            "population": city_data["population"],
            "ev_adoption_rate": round(random.uniform(0.01, 0.15), 3),
            "avg_income": random.randint(5000, 20000),
            "urbanization_rate": round(random.uniform(0.65, 0.95), 2),
            "avg_age": random.randint(32, 45),
            "public_transport_usage": round(random.uniform(0.1, 0.6), 2),
            "tourism_score": random.randint(1, 10),
            "growth_potential": round(random.uniform(0.01, 0.08), 3)
        }
        demographic_data.append(data)
    
    return pd.DataFrame(demographic_data)

def generate_traffic_data(cities):
    """Şehirler için trafik verisi oluşturur."""
    traffic_data = []
    
    for city_name, city_data in cities.items():
        data = {
            "city": city_name,
            "avg_daily_traffic": int(city_data["population"] * random.uniform(0.1, 0.4)),
            "peak_hour_factor": round(random.uniform(1.5, 3.5), 1),
            "highway_accessibility": round(random.uniform(0.3, 0.9), 2),
            "congestion_index": round(random.uniform(1.0, 10.0), 1),
            "avg_commute_time": random.randint(15, 60),
            "major_routes_count": random.randint(3, 15),
            "traffic_growth_rate": round(random.uniform(0.01, 0.08), 3)
        }
        traffic_data.append(data)
    
    return pd.DataFrame(traffic_data)

def generate_competitor_analysis(charging_stations):
    """Rakip analizi verileri oluşturur."""
    operators = charging_stations["operator"].unique()
    
    competitor_data = []
    for operator in operators:
        stations = charging_stations[charging_stations["operator"] == operator]
        
        data = {
            "operator": operator,
            "total_stations": len(stations),
            "avg_charger_count": round(stations["charger_count"].mean(), 1),
            "avg_power": round(stations["power_kw"].mean(), 1),
            "market_share": round(len(stations) / len(charging_stations), 3),
            "avg_customer_rating": round(stations["customer_rating"].mean(), 1),
            "expansion_rate": round(random.uniform(0.05, 0.3), 2),
            "pricing_tier": random.choice(["Ekonomik", "Orta", "Premium"]),
            "brand_recognition": random.randint(1, 10)
        }
        competitor_data.append(data)
    
    return pd.DataFrame(competitor_data)

def generate_all_data():
    """Tüm veri setlerini oluşturur ve sözlük olarak döndürür."""
    cities = generate_cities()
    charging_stations = generate_charging_stations(cities)
    demographic_data = generate_demographic_data(cities)
    traffic_data = generate_traffic_data(cities)
    competitor_data = generate_competitor_analysis(charging_stations)
    
    return {
        "cities": cities,
        "charging_stations": charging_stations,
        "demographic_data": demographic_data,
        "traffic_data": traffic_data,
        "competitor_data": competitor_data
    }

if __name__ == "__main__":
    # Test amaçlı - bu modül doğrudan çalıştırıldığında örnek veriler oluşturur
    data = generate_all_data()
    print(f"Oluşturulan şarj istasyonu sayısı: {len(data['charging_stations'])}")
    print(data['charging_stations'].head()) 