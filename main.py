# import pkg
from ast import Str
from email.header import Header
from re import I
from secrets import choice
from tkinter import W, Button
from tkinter.tix import Tree
from traceback import print_tb
import streamlit as st
import mysql.connector
import pandas as p
import numpy as np
from functools import reduce

# AHP
from pyDecision.algorithm import ahp_method

# database connection
DB = mysql.connector.connect(
    host = "localhost",
    port = "3307",
    username = "root",
    password = "root123",
    database  = "ahp_db"
)

# get data
def get(q):
    c = DB.cursor()
    c.execute(q)
    result = c.fetchall()
    return result

# get data
def getVal(q, val):
    c = DB.cursor()
    c.execute(q, val)
    k = c.fetchall()
    df = p.DataFrame(k)
    result = df.to_numpy()
    return result

# post data
def post(q, val):
    c = DB.cursor()
    c.execute(q, val)
    DB.commit()
    st.success("Data berhasil ditambah.")

# update data
def update(q):
    c = DB.cursor()
    query = "UPDATE karyawan SET disable = TRUE WHERE id = %s"
    val = [str(q)]
    c.execute(query, val)
    DB.commit()

# form create karyawan
def form_karyawan():
    st.write("Input Data Karyawan")
    with st.form(key="karyn_form", clear_on_submit=False):
        nama = st.text_input("Nama karyawan : ")
        kode = st.text_input("Kode karyawan : ")
        submit = st.form_submit_button(label="Tambah")
        if submit == True:
            if nama == "" or kode == "":
                st.error("Data tidak boleh kosong.") 
            else :
                val = [nama, kode]
                post("INSERT INTO karyawan (nama, kode) VALUES (%s, %s)", val)

# display karyawan
def display_karyawan():
    st.header("List Karyawan")
    d = get("SELECT * FROM karyawan WHERE disable = FALSE")
    df = p.DataFrame(d)
    arr = df.to_numpy()

    colms = st.columns((1, 3, 1, 2, 2, 2))
    fields = ["No", "Nama", "Kode", "Create_at", "Updated_at", "Action"]
    for col, field_name in zip(colms, fields):
        col.write(field_name)
    i = 0
    for data in arr:
        col1, col2, col3, col4, col5, col6 = st.columns((1, 3, 1, 2, 2, 2))
        i = i+1
        col1.write(str(i))
        col2.write(data[1])
        col3.write(data[2])
        col4.write(data[3])
        col5.write(data[4])
        button_phold = col6.empty()
        do_action = button_phold.button("Delete", key=i)
        if do_action:
            update(data[0])
            st.experimental_rerun()

# AHP method
def ahp_method(dataset, wd = 'm'):
        inc_rat  = np.array([0, 0, 0, 0.5245, 0.8815, 1.1086, 1.2479, 1.3417, 1.4056])
        X        = np.copy(dataset)
        weights  = np.zeros(X.shape[1])
        if (wd == 'm' or wd == 'mean'):
            weights  = np.mean(X/np.sum(X, axis = 0), axis = 1)
        elif (wd == 'g' or wd == 'geometric'):
            for i in range (0, X.shape[1]):
                weights[i] = reduce( (lambda x, y: x * y), X[i,:])**(1/X.shape[1])
            weights = weights/np.sum(weights)      
        vector   = np.sum(X*weights, axis = 1)/weights
        lamb_max = np.mean(vector)
        cons_ind = (lamb_max - X.shape[1])/(X.shape[1] - 1)
        rc       = cons_ind/inc_rat[X.shape[1]]
        return weights, rc

def init_ahp():
    # AHP

    # Parameters
    weight_derivation = 'mean' # 'mean' or 'geometric'

    # Dataset
    dataset = np.array([
        #g1     g2     g3     g4     g5     g6     g7   g8               
        [1  ,   3  ,   3  ,   3  ,   5  ,   5  ,   6  , 6],   #g1 KPI
        [1/3,   1  ,   2  ,   2  ,   3  ,   3  ,   4  , 5],   #g2 analisis data
        [1/3,   1/2,   1  ,   1  ,   1/2,   4  ,   4  , 5],   #g3 berpikir kritis
        [1/3,   1/2,   1  ,   1  ,   1  ,   3  ,   4  , 4],   #g4 kreatifitas inovasi
        [1/5,   1/3,   2  ,   1  ,   1  ,   2  ,   3  , 4],   #g5 komunikasi
        [1/5,   1/3,   1/4,   1/3,   1/2,   1  ,   3  , 3],   #g6 kerjasama
        [1/6,   1/4,   1/4,   1/4,   1/3,   1/3,   1  , 1],   #g7 sikap
        [1/6,   1/5,   1/5,   1/4,   1/4,   1/3,   1  , 1]    #g8 absen
    ])

    # Call AHP Function
    weights, rc = ahp_method(dataset, wd = weight_derivation)

    k = []
    for i in range(0, weights.shape[0]):
        k.append(round(weights[i], 3))
    
    return k

# form penilaian
# def checkNilai():
#     st.header("Input Nilai")
#     # col1, col2, col3, col4 = st.columns(4)
#     m = ("Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember")
#     k = get("SELECT id, nama FROM karyawan WHERE disable = 0")
#     df = p.DataFrame(k)
#     kr = df.to_numpy()
#     namaKr = []
#     for val in kr:
#         namaKr.append(val[1])
#     with st.form(key="check"):
#         year = st.selectbox('Tahun', range(2019, 2025), index=3)
#         month = st.selectbox('Month', m)
#         karyawan = st.selectbox('Karyawan', namaKr)
#         cek = st.form_submit_button(label="Check")
#         if cek:
#             for val in kr:
#                 if(val[1] == karyawan):
#                     id = val[0] 
#                     break
#             q = "SELECT d.id_karyawan FROM detail_penilaian d LEFT JOIN penilaian p on d.id_penilaian = p.id WHERE p.bulan = %s AND p.tahun = %s AND d.id_karyawan = %s"
#             val = (month, str(year), str(id))
#             c = DB.cursor()
#             c.execute(q, val)
#             k = c.fetchall()
#             return k

def formNilai():
    m = ("Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember")

    k = get("SELECT id, nama FROM karyawan WHERE disable = 0")

    df = p.DataFrame(k)
    kr = df.to_numpy()

    namaKr = []
    for val in kr:
        namaKr.append(val[1])

    kriteria = ["Key Performance Indicator (KPI)", "Analisis data", "Berfikir kritis", "Kreatif  dan inovatif", "Komunikasi", "Kerjasama", "Sikap", "Absensi"]

    st.header("Nilai Per Kriteria")
    raw = [0 for i in range(len(kriteria))]
    k = [0 for i in range(len(kriteria))]
    nilai = ("Kurang", "Cukup", "Baik", "Sangat Baik")

    with st.form(key="form_nilai", clear_on_submit=True):
        st.header("Detail")
        year = st.selectbox('Tahun', range(2019, 2025), index=3)
        karyawan = st.selectbox('Karyawan', namaKr)
        st.header("Input Nilai")
        raw[0] = st.selectbox(kriteria[0], nilai)
        raw[1] = st.selectbox(kriteria[1], nilai)
        raw[2] = st.selectbox(kriteria[2], nilai)
        raw[3] = st.selectbox(kriteria[3], nilai)
        raw[4] = st.selectbox(kriteria[4], nilai)
        raw[5] = st.selectbox(kriteria[5], nilai)
        raw[6] = st.selectbox(kriteria[6], nilai)
        raw[7] = st.selectbox(kriteria[7], nilai)
        done = st.form_submit_button(label="Selesai")

        if done:
            for val in kr:
                if(val[1] == karyawan):
                    id_kr = val[0] 
                    break
            q = "SELECT d.id_karyawan FROM detail_penilaian d LEFT JOIN penilaian p on d.id_penilaian = p.id WHERE p.tahun = %s AND d.id_karyawan = %s"
            val = [str(year), str(id_kr)]
            kr = getVal(q, val)
            if len(kr) != 0:
                st.warning('Karyawan pada tahun ini sudah dinilai.', icon="⚠️")
                return
            i = 0
            for r in raw:
                for j in range(0, len(nilai)):
                    if r == nilai[j]:
                        k[i] = j+1
                        i = i + 1
                        break
            q = "SELECT id FROM penilaian WHERE tahun = %s"
            val = [str(year)]
            id_pn = getVal(q, val)
            if len(id_pn) == 0:
                q = "INSERT INTO penilaian (tahun) VALUES(%s)"
                val = [str(year)]
                post(q, val)

                q = "SELECT id FROM penilaian WHERE tahun = %s"
                val = [str(year)]
                id_pn = getVal(q, val)
            q = "INSERT INTO detail_penilaian(id_karyawan, id_penilaian, k1, k2, k3, k4, k5, k6, k7, k8) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            val = [str(id_kr), str(id_pn[0][0]), str(k[0]), str(k[1]), str(k[2]), str(k[3]), str(k[4]), str(k[5]), str(k[6]), str(k[7])]
            post(q, val)
            
            

# display penilaian
def displayPenilaian():
    st.header("Penilaian Karyawan")
    col1, col2 = st.columns(2)
    with col1:
        year = st.selectbox('Tahun', range(2019, 2025), index=3)
    q = "SELECT k.id, k.nama, k.kode, d.k1, d.k2, d.k3, d.k4, d.k5, d.k6, d.k7, d.k8 FROM detail_penilaian d LEFT JOIN karyawan k on d.id_karyawan = k.id LEFT JOIN penilaian p on d.id_penilaian = p.id WHERE p.tahun = %s"
    val = [str(year)]
    dat = getVal(q, val)
    q  = "SELECT id FROM karyawan"
    kr = get(q)
    if len(dat) != len(kr):
        st.warning('Nilai karyawan belum lengkap.', icon="⚠️")
    else :
        # nilai = {1:"Kurang", 2:"Cukup", 3:"Baik", 4:"Sangat Baik"}
        colms = st.columns((1, 3, 2, 1, 1, 1, 1, 1, 1, 1, 1))
        fields = ["No", "Nama", "Kode", "K1", "K2", "K3", "K4", "K5", "K6", "K7", "K8"]
        for col, field_name in zip(colms, fields):
            col.write(field_name)
        i = 0
        for val in dat:
            col1, col2, col3, col4, col5, col6, col7, col8, col9, col10, col11 = st.columns((1, 3, 2, 1, 1, 1, 1, 1, 1, 1, 1))
            i = i+1
            col1.write(str(i))
            col2.write(str(val[1]))
            col3.write(str(val[2]))
            col4.write(str(val[3]))
            col5.write(str(val[4]))
            col6.write(str(val[5]))
            col7.write(str(val[6]))
            col8.write(str(val[7]))
            col9.write(str(val[8]))
            col10.write(str(val[9]))
            col11.write(str(val[10]))
        colm1, colm2 = st.columns(2)
        with colm1:
            st.write('''
            ### **Keterangan**
            K1 -> Key Performance Indicator (KPI)
            
            K2 -> Analisis data
            
            K3 -> Berfikir kritis
            
            K4 -> Kreatif  dan inovatif
            
            K5 -> Komunikasi
            
            K6 -> Kerjasama
            
            K7 -> Sikap
            
            K8 -> Absensi
            ''')
        with colm2:
            st.write('''
            ## .
            4 -> Sangat Baik
            
            3 -> Baik
            
            2 -> Cukup
            
            1 -> Kurang
            ''')

# menentukan peringkat
def ranking(bobot):
    col1, col2 = st.columns(2)
    with col1:
        year = st.selectbox('Tahun', range(2019, 2025), index=3)
    with col2:
        gaji = st.number_input("Gaji Banus")
    cek = st.button("Check")
    if cek :
        q = "SELECT k.id, k.nama, k.kode, d.k1, d.k2, d.k3, d.k4, d.k5, d.k6, d.k7, d.k8 FROM detail_penilaian d LEFT JOIN karyawan k on d.id_karyawan = k.id LEFT JOIN penilaian p on d.id_penilaian = p.id WHERE p.tahun = %s"
        val = [str(year)]
        dat = getVal(q, val)
        q  = "SELECT id FROM karyawan"
        kr = get(q)
        if len(dat) != len(kr) or gaji < 1:
            st.warning('Nilai karyawan belum lengkap atau nilai gaji bonus kosong.', icon="⚠️")
        else :
            # normalisasi nilai
            sum = []
            for val in dat:
                s = 0
                for i in range(3, 11):
                    val[i] = val[i]/4
                    val[i] = round(val[i] * bobot[i - 3], 3)
                    s += val[i]
                sum.append(round(s, 3))
            # kali dengan bobot

            # debug
            colms = st.columns((1, 3, 2, 2, 2))
            fields = ["Rank", "Nama", "Kode","Performance", "Gaji Bonus"]
            for col, field_name in zip(colms, fields):
                col.write(field_name)
            
            i = 0
            toSort = []
            for val in dat:
                data = [val[1], val[2], val[3], val[4], val[5], val[6], val[7], val[9], val[9], val[10], sum[i]]
                toSort.append(data)
                i = i+1
            toSort.sort(key=lambda i: i[len(toSort)-1], reverse=True)
            
            i = 0
            for val in toSort:
                col1, col2, col3, col4, col12 = st.columns((1, 3, 2, 2, 2))
                i = i+1
                col1.write(str(i))
                col2.write(str(val[0]))
                col3.write(str(val[1]))
                col4.write(str(val[10]))
                if val[10] < 0.7:
                    col12.write(str(0))
                else:
                    col12.write(str(val[10] * gaji))
            

# main function
def main():
    st.header("Sistem Pendukung Keputusan Penerima Bonus Gaji Karyawan PT. Sadhana Adiwidya Bhuana")
    menu = ["Home", "Tambah Karyawan", "Karyawan", "Input Nilai", "Penilaian", "Gaji Bonus Karyawan", "Login"]
    choice = st.sidebar.selectbox("MENU", menu)
    if choice == "Home":
        st.write('''
        # Hai
        # Selamat Datang
        ''')
    if choice == "Tambah Karyawan":
        form_karyawan()
    if choice == "Karyawan":
        display_karyawan()
    if choice == "Input Nilai":
        formNilai()
    if choice == "Penilaian":
        displayPenilaian()
    if choice == "Login":
        st.header("Masukkan Username dan Password")
        with st.form(key="login"):
            st.text_input("Username")
            st.text_input(label="Password", type="password")
            st.form_submit_button("Login")
    if choice == "Gaji Bonus Karyawan":
        k = init_ahp()
        ranking(k)
        

if __name__ == '__main__':  
    main()