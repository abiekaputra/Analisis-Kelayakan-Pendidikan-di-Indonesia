import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns
import streamlit as st
import geopandas as gpd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
from adjustText import adjust_text

st.title('Analisis Kelayakan Pendidikan di Indonesia')
st.write("Visualisasi data kelayakan pendidikan di Indonesia berdasarkan berbagai indikator seperti jumlah siswa mengulang, putus sekolah, dan kondisi ruang kelas.")

file_path = 'data/kelayakan-pendidikan-indonesia.csv'
data = pd.read_csv(file_path)

st.write("Berikut beberapa baris pertama dari dataset:")
st.write(data.head())

st.write("Jumlah data yang hilang di setiap kolom:")
missing_values = data.isnull().sum()
st.write(missing_values)

data = data.fillna(0)

numeric_columns = ['Sekolah', 'Siswa', 'Mengulang', 'Putus Sekolah', 
                   'Kepala Sekolah dan Guru(<S1)', 'Kepala Sekolah dan Guru(≥ S1)',
                   'Tenaga Kependidikan(SM)', 'Tenaga Kependidikan(>SM)',
                   'Rombongan Belajar', 'Ruang kelas(baik)', 
                   'Ruang kelas(rusak ringan)', 'Ruang kelas(rusak sedang)', 'Ruang kelas(rusak berat)']
data[numeric_columns] = data[numeric_columns].apply(pd.to_numeric)
data['Provinsi'] = data['Provinsi'].str.strip()

st.write("Statistik deskriptif:")
descriptive_stats = data[numeric_columns].describe()
st.write(descriptive_stats)

# Correlation matrix heatmap
st.write("Matrix korelasi antar indikator:")
correlation_matrix = data[numeric_columns].corr()
fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', linewidths=0.5)
plt.title("Correlation Matrix")
st.pyplot(fig)

# Outliers detection
st.write("Deteksi outlier untuk 'Mengulang' dan 'Putus Sekolah':")
Q1 = data[['Mengulang', 'Putus Sekolah']].quantile(0.25)
Q3 = data[['Mengulang', 'Putus Sekolah']].quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR
outliers = data[(data['Mengulang'] < lower_bound['Mengulang']) | (data['Mengulang'] > upper_bound['Mengulang']) |
                (data['Putus Sekolah'] < lower_bound['Putus Sekolah']) | (data['Putus Sekolah'] > upper_bound['Putus Sekolah'])]

st.write("Provinsi dengan outliers:")
st.write(outliers[['Provinsi', 'Mengulang', 'Putus Sekolah']])

# Visualisasi outliers
fig, ax = plt.subplots(figsize=(10, 6))
sns.boxplot(data=data[['Mengulang', 'Putus Sekolah']])
texts = []
for i in range(outliers.shape[0]):
    texts.append(plt.text(0, outliers['Mengulang'].iloc[i], outliers['Provinsi'].iloc[i], 
                          horizontalalignment='left', color='blue', size='small', weight='semibold'))
    texts.append(plt.text(1, outliers['Putus Sekolah'].iloc[i], outliers['Provinsi'].iloc[i], 
                          horizontalalignment='left', color='blue', size='small', weight='semibold'))
adjust_text(texts, only_move={'points': 'y', 'texts': 'y'}, arrowprops=dict(arrowstyle='->', color='white', lw=0.5))
plt.title("Outliers untuk Mengulang dan Putus Sekolah")
st.pyplot(fig)

# Interactive selection for plotting bar chart
st.write("Pilih kolom yang ingin divisualisasikan untuk bar chart:")
bar_column = st.selectbox("Pilih kolom", numeric_columns)

fig, ax = plt.subplots(figsize=(10, 6))
data_sorted = data.sort_values(by=bar_column, ascending=False)
bars = plt.barh(data_sorted['Provinsi'], data_sorted[bar_column], color='#4a90e2')
plt.xlabel(bar_column)
plt.ylabel('Provinsi')
plt.title(f'Jumlah {bar_column} di Setiap Provinsi')
st.pyplot(fig)

# Scatter plot Ruang kelas rusak berat dan Mengulang
st.write("Scatter plot: Hubungan antara ruang kelas rusak berat dan siswa mengulang.")
fig, ax = plt.subplots(figsize=(8, 6))
plt.scatter(data['Ruang kelas(rusak berat)'], data['Mengulang'], color='#3498db', label='Siswa Mengulang')
plt.scatter(data['Ruang kelas(rusak berat)'][data['Mengulang'] > data['Mengulang'].quantile(0.75)], 
            data['Mengulang'][data['Mengulang'] > data['Mengulang'].quantile(0.75)], 
            color='#e74c3c', label='Outliers')
plt.xlabel('Ruang Kelas Rusak Berat')
plt.ylabel('Jumlah Siswa Mengulang')
plt.title('Hubungan Antara Ruang Kelas Rusak Berat dan Siswa Mengulang')
plt.legend()
st.pyplot(fig)

# Clustering using KMeans
st.write("Hasil clustering berdasarkan kondisi pendidikan:")
X = data[['Ruang kelas(rusak berat)', 'Mengulang']]
kmeans = KMeans(n_clusters=3, random_state=0).fit(X)
data['Cluster'] = kmeans.labels_
fig, ax = plt.subplots(figsize=(8, 6))
sns.scatterplot(x='Ruang kelas(rusak berat)', y='Mengulang', hue='Cluster', data=data, palette='Set1')
plt.title('K-Means Clustering: Mengelompokkan Provinsi Berdasarkan Kondisi Pendidikan')
plt.xlabel('Ruang Kelas Rusak Berat')
plt.ylabel('Jumlah Siswa Mengulang')
st.pyplot(fig)

# Display cluster data
cluster_selection = st.selectbox("Pilih Cluster untuk melihat daftar provinsi:", [0, 1, 2])
selected_cluster = data[data['Cluster'] == cluster_selection]['Provinsi']
st.write(f"Provinsi di Cluster {cluster_selection}:")
st.write(selected_cluster.to_string(index=False))

# Visualisasi geospasial dengan shapefile
gdf = gpd.read_file('data/gadm41_IDN_1.shp')
gdf = gdf.rename(columns={'NAME_1': 'Provinsi'})

data_pendidikan = pd.read_csv("data/kelayakan-pendidikan-indonesia.csv")

# Menghapus awalan 'Prov.' dari kolom 'Provinsi' di dataset pendidikan
data_pendidikan['Provinsi'] = data_pendidikan['Provinsi'].str.replace("Prov. ", "")

# Mapping nama provinsi agar sesuai dengan shapefile
provinsi_mapping = {
    'D.K.I. Jakarta': 'Jakarta',
    'D.I. Yogyakarta': 'Yogyakarta',
    'Sumatera Utara': 'Sumatera Utara',
    'Jawa Barat': 'Jawa Barat',
    'Jawa Tengah': 'Jawa Tengah',
    'Jawa Timur': 'Jawa Timur',
    'Aceh': 'Aceh',
    'Sumatera Barat': 'Sumatera Barat',
    'Riau': 'Riau',
    'Jambi': 'Jambi',
    'Sumatera Selatan': 'Sumatera Selatan',
    'Lampung': 'Lampung',
    'Kalimantan Barat': 'Kalimantan Barat',
    'Kalimantan Tengah': 'Kalimantan Tengah',
    'Kalimantan Selatan': 'Kalimantan Selatan',
    'Kalimantan Timur': 'Kalimantan Timur',
    'Sulawesi Utara': 'Sulawesi Utara',
    'Sulawesi Tengah': 'Sulawesi Tengah',
    'Sulawesi Selatan': 'Sulawesi Selatan',
    'Sulawesi Tenggara': 'Sulawesi Tenggara',
    'Maluku': 'Maluku',
    'Bali': 'Bali',
    'Nusa Tenggara Barat': 'Nusa Tenggara Barat',
    'Nusa Tenggara Timur': 'Nusa Tenggara Timur',
    'Papua': 'Papua',
    'Bengkulu': 'Bengkulu',
    'Maluku Utara': 'Maluku Utara',
    'Banten': 'Banten',
    'Kepulauan Bangka Belitung': 'Kepulauan Bangka Belitung',
    'Gorontalo': 'Gorontalo',
    'Kepulauan Riau': 'Kepulauan Riau',
    'Papua Barat': 'Papua Barat',
    'Sulawesi Barat': 'Sulawesi Barat',
    'Kalimantan Utara': 'Kalimantan Utara',
    'Papua Tengah': 'Papua Tengah',
    'Papua Selatan': 'Papua Selatan',
    'Papua Pegunungan': 'Papua Pegunungan',
    'Papua Barat Daya': 'Papua Barat Daya'
}

# Mengganti nama provinsi di dataset pendidikan agar sesuai dengan shapefile
data_pendidikan['Provinsi'] = data_pendidikan['Provinsi'].replace(provinsi_mapping)
provinsi_to_remove = ['Luar Negeri', 'Papua Tengah', 'Papua Selatan', 'Papua Pegunungan', 'Papua Barat Daya']
data_pendidikan_filtered = data_pendidikan[~data_pendidikan['Provinsi'].isin(provinsi_to_remove)]

# Menggabungkan shapefile dengan data pendidikan berdasarkan provinsi
merged_data = gdf.merge(data_pendidikan_filtered, on='Provinsi', how='left')
missing_geometry = merged_data[merged_data['geometry'].isna()]
if not missing_geometry.empty:
    st.write("Provinsi dengan geometri yang hilang:")
    st.write(missing_geometry['Provinsi'].tolist())

merged_data = merged_data.dropna(subset=['geometry'])

# Visualisasi peta geospasial
st.write("Distribusi ruang kelas rusak berat di Indonesia:")
fig, ax = plt.subplots(1, 1, figsize=(12, 10))
merged_data.plot(column='Ruang kelas(rusak berat)', cmap='Spectral', linewidth=0.8, ax=ax, edgecolor='0.8', legend=True)
plt.title('Distribusi Ruang Kelas Rusak Berat di Indonesia Berdasarkan Provinsi', fontsize=16, pad=20)
plt.figtext(0.5, 0.03, 'Sumber: Dataset Kelayakan Pendidikan Indonesia', ha='center', fontsize=12)
plt.figtext(0.5, 0.01, 'Provinsi dengan lebih banyak ruang kelas rusak berat ditandai dengan warna lebih gelap', ha='center', fontsize=10)
ax.set_axis_off()
st.pyplot(fig)

# Simulasi Penambahan Ruang Kelas
st.write("Simulasi penambahan ruang kelas dan pengurangan siswa mengulang:")
n_simulasi = 1000
simulasi_hasil = []
for i in range(n_simulasi):
    penambahan_kelas = np.random.uniform(0, 500)
    pengurangan_mengulang = penambahan_kelas * np.random.uniform(0.05, 0.1)
    simulasi_hasil.append(pengurangan_mengulang)

fig, ax = plt.subplots(figsize=(8, 6))
plt.hist(simulasi_hasil, bins=30, color='mediumseagreen')
plt.title('Distribusi Pengurangan Siswa Mengulang Berdasarkan Penambahan Ruang Kelas', fontsize=14)
plt.xlabel('Pengurangan Siswa Mengulang', fontsize=12)
plt.ylabel('Frekuensi', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.7)
st.pyplot(fig)