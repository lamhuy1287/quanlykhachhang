import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import sqlite3
from tkinter.filedialog import askopenfilename

# Khởi tạo CSDL nếu chưa có
def init_db():
    conn = sqlite3.connect("khachhang.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS khachhang (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ten TEXT NOT NULL,
                        tien_hang REAL,
                        tien_con_thieu REAL,
                        file_cart TEXT,
                        trang_thai TEXT,
                        ngay_mua TEXT)''')
    conn.commit()
    conn.close()

init_db()

# Hàm thêm khách hàng
def them_khach_hang():
    ten = entry_ten.get()
    tien_hang = entry_tienhang.get()
    tien_thieu = entry_tienthieu.get()
    file_cart = entry_file.get()
    trang_thai = combo_trangthai.get()
    ngay_mua = entry_ngaymua.get()

    if ten == "" or tien_hang == "" or tien_thieu == "" or file_cart == "":
        messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đầy đủ thông tin.")
        return

    try:
        conn = sqlite3.connect("khachhang.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO khachhang (ten, tien_hang, tien_con_thieu, file_cart, trang_thai, ngay_mua) VALUES (?, ?, ?, ?, ?, ?)",
                       (ten, tien_hang, tien_thieu, file_cart, trang_thai, ngay_mua))
        conn.commit()
        conn.close()
        hien_thi()
        xoa_form()
    except Exception as e:
        messagebox.showerror("Lỗi", str(e))

# Hàm hiển thị danh sách khách hàng
def hien_thi():
    for i in tree.get_children():
        tree.delete(i)
    conn = sqlite3.connect("khachhang.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM khachhang")
    rows = cursor.fetchall()
    for row in rows:
        tree.insert("", "end", values=row)
    conn.close()

# Xóa form nhập thông tin
def xoa_form():
    entry_ten.delete(0, tk.END)
    entry_tienhang.delete(0, tk.END)
    entry_tienthieu.delete(0, tk.END)
    entry_file.delete(0, tk.END)
    combo_trangthai.set("chưa thanh toán đủ")
    entry_ngaymua.delete(0, tk.END)

# Cập nhật trạng thái thanh toán
def cap_nhat_trang_thai():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Chọn dòng", "Vui lòng chọn khách hàng.")
        return

    item = tree.item(selected)
    id_kh = item['values'][0]
    trang_thai_ht = item['values'][5]

    if trang_thai_ht == "đã thanh toán đủ":
        messagebox.showinfo("Không thể sửa", "Khách hàng đã thanh toán đủ, không được sửa.")
        return

    result = messagebox.askyesno("Xác nhận", "Xác nhận đã thanh toán đủ?")
    if result:
        conn = sqlite3.connect("khachhang.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE khachhang SET trang_thai = 'đã thanh toán đủ' WHERE id = ?", (id_kh,))
        conn.commit()
        conn.close()
        hien_thi()

# Xoá khách hàng
def xoa_khach_hang():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Chọn dòng", "Vui lòng chọn khách hàng.")
        return

    item = tree.item(selected)
    id_kh = item['values'][0]

    result = messagebox.askyesno("Xác nhận", "Xác nhận xoá khách hàng này?")
    if result:
        conn = sqlite3.connect("khachhang.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM khachhang WHERE id = ?", (id_kh,))
        conn.commit()
        conn.close()
        hien_thi()

# Tìm kiếm khách hàng
def tim_kiem():
    keyword = entry_timkiem.get()
    if not keyword:
        messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập từ khoá tìm kiếm.")
        return
    
    for i in tree.get_children():
        tree.delete(i)
    
    conn = sqlite3.connect("khachhang.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM khachhang WHERE ten LIKE ?", ('%' + keyword + '%',))
    rows = cursor.fetchall()
    for row in rows:
        tree.insert("", "end", values=row)
    conn.close()

# Chọn file cart
def chon_file():
    file_path = askopenfilename(title="Chọn file cart", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    if file_path:
        entry_file.delete(0, tk.END)
        entry_file.insert(0, file_path)

# Giao diện chính
root = tk.Tk()
root.title("🧾 Phần mềm Quản lý Khách Hàng")
root.geometry("1280x720")
root.state('zoomed')  # Chế độ full màn hình
root.resizable(True, True)

# Khung tiêu đề
title = tk.Label(root, text="PHẦN MỀM QUẢN LÝ KHÁCH HÀNG", font=("Helvetica", 18, "bold"), fg="#1a73e8")
title.pack(pady=10)

# Thanh tìm kiếm
frame_search = tk.Frame(root)
frame_search.pack(pady=10, padx=10, fill="x")

tk.Label(frame_search, text="Tìm kiếm khách hàng:", font=("Arial", 12)).pack(side=tk.LEFT, padx=10)
entry_timkiem = tk.Entry(frame_search, font=("Arial", 12), width=40)
entry_timkiem.pack(side=tk.LEFT, padx=10)
tk.Button(frame_search, text="🔍 Tìm kiếm", font=("Arial", 12), command=tim_kiem).pack(side=tk.LEFT, padx=10)

# Khung chính
frame_main = tk.Frame(root)
frame_main.pack(pady=10, padx=10, fill="both", expand=True)

# Form bên trái
frame_left = tk.LabelFrame(frame_main, text="Nhập thông tin", padx=10, pady=10)
frame_left.grid(row=0, column=0, sticky="n")

tk.Label(frame_left, text="Tên khách hàng:").grid(row=0, column=0, sticky="w")
entry_ten = tk.Entry(frame_left, width=30)
entry_ten.grid(row=0, column=1)

tk.Label(frame_left, text="Tiền hàng:").grid(row=1, column=0, sticky="w")
entry_tienhang = tk.Entry(frame_left, width=30)
entry_tienhang.grid(row=1, column=1)

tk.Label(frame_left, text="Tiền còn thiếu:").grid(row=2, column=0, sticky="w")
entry_tienthieu = tk.Entry(frame_left, width=30)
entry_tienthieu.grid(row=2, column=1)

tk.Label(frame_left, text="File cart đơn hàng:").grid(row=3, column=0, sticky="w")
entry_file = tk.Entry(frame_left, width=30)
entry_file.grid(row=3, column=1)
tk.Button(frame_left, text="Chọn file", command=chon_file).grid(row=3, column=2, padx=5)

tk.Label(frame_left, text="Trạng thái:").grid(row=4, column=0, sticky="w")
combo_trangthai = ttk.Combobox(frame_left, values=["đã thanh toán đủ", "chưa thanh toán đủ"], state="readonly")
combo_trangthai.set("chưa thanh toán đủ")
combo_trangthai.grid(row=4, column=1)

tk.Label(frame_left, text="Ngày mua:").grid(row=5, column=0, sticky="w")
entry_ngaymua = DateEntry(frame_left, width=30)
entry_ngaymua.grid(row=5, column=1)

# Bảng hiển thị bên phải
frame_right = tk.LabelFrame(frame_main, text="Danh sách khách hàng", padx=10, pady=10)
frame_right.grid(row=0, column=1)

cols = ("ID", "Tên", "Tiền hàng", "Tiền còn thiếu", "File cart", "Ngày mua", "Trạng thái")
tree = ttk.Treeview(frame_right, columns=cols, show='headings', height=18)
for col in cols:
    tree.heading(col, text=col)
    tree.column(col, width=130 if col != "Tên" else 120)
tree.pack()

# Nút chức năng
frame_buttons = tk.Frame(root)
frame_buttons.pack(pady=10)

tk.Button(frame_buttons, text="➕ Thêm khách hàng", width=15, command=them_khach_hang).grid(row=0, column=0, padx=10)
tk.Button(frame_buttons, text="✔️ Cập nhật trạng thái", width=15, command=cap_nhat_trang_thai).grid(row=0, column=1, padx=10)
tk.Button(frame_buttons, text="🗑️ Xoá khách hàng", width=15, command=xoa_khach_hang).grid(row=0, column=2, padx=10)
tk.Button(frame_buttons, text="❌ Thoát", width=15, command=root.destroy).grid(row=1, column=0, columnspan=3, pady=10)

hien_thi()  # Hiển thị danh sách khi mở ứng dụng
root.mainloop()
