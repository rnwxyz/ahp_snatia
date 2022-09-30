# import pkg
from ast import Str
from re import I
from secrets import choice
from tkinter import Button
import streamlit as st
import mysql.connector
import pandas as p
import numpy as np
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

# post data
def post(nama, kode):
    c = DB.cursor()
    query = "INSERT INTO karyawan (nama, kode) VALUES (%s, %s)"
    val = [nama, kode]
    c.execute(query, val)
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
    with st.form(key="karyawan_form", clear_on_submit=True):
        nama = st.text_input("Nama karyawan : ")
        kode = st.text_input("Kode karyawan : ")
        submit = st.form_submit_button(label="Tambah")
        if submit == True:
            if nama == "" or kode == "":
                st.error("Data tidak boleh kosong.") 
            else :
                post(nama, kode)

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
        do_action = button_phold.button("Delete", key=data[0])
        if do_action:
            update(data[0])
            st.experimental_rerun()

def init_ahp():
    # AHP

    # Parameters
    weight_derivation = 'geometric' # 'mean' or 'geometric'

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


# main function
def main():
    st.title("Sistem Pendukung Keputusan Penerima Bonus Gaji Karyawan PT. Sadhana Adiwidya Bhuana")
    menu = ["Home", "Tambah Karyawan", "Karyawan", "Penilaian", "Rekomendasi"]
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
    if choice == "Penilaian":
        st.write("Penelitian")
    if choice == "Rekomendasi":
        st.header("Bobot kriteria")
        k = init_ahp()
        i = 0
        for w in k :
            i = i+1
            st.write('k'+str(i)+' = ', w)

if __name__ == '__main__':  
    main()