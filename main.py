import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
import sqlite3
from PIL import Image, ImageTk
import os
from io import BytesIO
from datetime import datetime

# Khởi tạo CSDL
def init_db():
    with sqlite3.connect("quanlybanhang.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS sanpham (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ma_sp TEXT UNIQUE,
                        ten_sp TEXT,
                        anh_sp BLOB,
                        gia_nhap REAL,
                        gia_ban REAL,
                        so_luong INTEGER)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS khachhang (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ten_kh TEXT,
                        danh_muc TEXT,
                        ngay_dat TEXT,
                        ngay_giao TEXT,
                        file_sp TEXT,
                        tong_tien REAL,
                        da_coc REAL,
                        con_thieu REAL GENERATED ALWAYS AS (tong_tien - da_coc) VIRTUAL,
                        trang_thai TEXT)''')
        conn.commit()

init_db()

class ImageManager:
    @staticmethod
    def resize_image(image_path, max_size=(100, 100)):
        try:
            img = Image.open(image_path)
            img.thumbnail(max_size)
            return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Error resizing image: {e}")
            return None
    
    @staticmethod
    def image_to_blob(image_path):
        try:
            img = Image.open(image_path)
            img.thumbnail((200, 200))
            with BytesIO() as output:
                img.save(output, format="PNG")
                return output.getvalue()
        except Exception as e:
            print(f"Error converting image to blob: {e}")
            return None
    
    @staticmethod
    def blob_to_image(blob_data):
        if blob_data is None or isinstance(blob_data, str):
            return None
        try:
            return ImageTk.PhotoImage(Image.open(BytesIO(blob_data)))
        except Exception as e:
            print(f"Error converting blob to image: {e}")
            return None

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("HỆ THỐNG QUẢN LÝ BÁN HÀNG")
        self.root.geometry("1280x720")
        self.root.state('zoomed')
        self.setup_main_frame()
    
    def setup_main_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill="both", expand=True)
        
        tk.Label(main_frame, text="HỆ THỐNG QUẢN LÝ BÁN HÀNG", 
                font=("Arial", 24, "bold"), bg="#f0f0f0", fg="#2c3e50").pack(pady=50)
        
        btn_frame = tk.Frame(main_frame, bg="#f0f0f0")
        btn_frame.pack(pady=50)
        
        tk.Button(btn_frame, text="QUẢN LÝ SẢN PHẨM", width=25, height=3,
                 font=("Arial", 14), command=self.open_product_manager, bg="#3498db", fg="black").grid(row=0, column=0, padx=20)
        tk.Button(btn_frame, text="QUẢN LÝ ĐƠN HÀNG", width=25, height=3,
                 font=("Arial", 14), command=self.open_order_manager, bg="#2ecc71", fg="black").grid(row=0, column=1, padx=20)
        tk.Button(btn_frame, text="THOÁT", width=25, height=3,
                 font=("Arial", 14), command=self.root.quit, bg="#e74c3c", fg="black").grid(row=0, column=2, padx=20)
    
    def open_product_manager(self):
        ProductManager(self.root)
    
    def open_order_manager(self):
        OrderManager(self.root)

class ProductManager:
    def __init__(self, root):
        self.root = root
        self.image_references = []
        self.setup_ui()
        self.load_products()
    
    def setup_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        tk.Label(main_frame, text="QUẢN LÝ SẢN PHẨM", font=("Arial", 18, "bold")).pack(pady=10)
        
        toolbar = tk.Frame(main_frame)
        toolbar.pack(fill="x", pady=10)
        
        tk.Button(toolbar, text="Thêm sản phẩm", command=self.add_product_dialog).pack(side="left", padx=5)
        tk.Button(toolbar, text="Sửa sản phẩm", command=self.edit_product).pack(side="left", padx=5)
        tk.Button(toolbar, text="Xóa sản phẩm", command=self.delete_product).pack(side="left", padx=5)
        tk.Button(toolbar, text="Quay lại", command=lambda: MainApp(self.root)).pack(side="right", padx=5)
        
        # Thêm ô tìm kiếm
        tk.Label(toolbar, text="Tìm kiếm:").pack(side="left", padx=5)
        self.search_var = tk.StringVar()
        tk.Entry(toolbar, textvariable=self.search_var).pack(side="left", padx=5)
        tk.Button(toolbar, text="Tìm", command=self.search_products).pack(side="left", padx=5)
        tk.Button(toolbar, text="Hủy tìm kiếm", command=self.load_products).pack(side="left", padx=5)
        
        columns = ("ID", "Mã SP", "Tên SP", "Ảnh", "Giá nhập", "Giá bán", "Số lượng")
        self.tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=20)
        
        self.tree.column("ID", width=50)
        self.tree.column("Mã SP", width=100)
        self.tree.column("Tên SP", width=200)
        self.tree.column("Ảnh", width=120)
        self.tree.column("Giá nhập", width=100)
        self.tree.column("Giá bán", width=100)
        self.tree.column("Số lượng", width=80)
        
        for col in columns:
            self.tree.heading(col, text=col)
        
        self.tree.pack(fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(self.tree, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.bind("<Double-1>", self.show_full_image)
    
    def load_products(self):
        self.image_references.clear()
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        with sqlite3.connect("quanlybanhang.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, ma_sp, ten_sp, anh_sp, gia_nhap, gia_ban, so_luong FROM sanpham")
            products = cursor.fetchall()
        
        for product in products:
            img_data = product[3]
            img_preview = "Nhấn đúp 2 lần để xem hình ảnh" if img_data and not isinstance(img_data, str) else "Không có ảnh"
            if img_data and not isinstance(img_data, str):
                img = ImageManager.blob_to_image(img_data)
                if img:
                    self.image_references.append(img)
            
            self.tree.insert("", "end", values=(
                product[0], product[1], product[2], 
                img_preview,
                f"{product[4]:,.0f}đ", 
                f"{product[5]:,.0f}đ", 
                product[6]
            ))
    
    def search_products(self):
        query = self.search_var.get().strip().lower()
        if not query:
            self.load_products()
            return
        
        self.image_references.clear()
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        with sqlite3.connect("quanlybanhang.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, ma_sp, ten_sp, anh_sp, gia_nhap, gia_ban, so_luong FROM sanpham "
                          "WHERE LOWER(ma_sp) LIKE ? OR LOWER(ten_sp) LIKE ?",
                          (f"%{query}%", f"%{query}%"))
            products = cursor.fetchall()
        
        for product in products:
            img_data = product[3]
            img_preview = "Nhấn đúp 2 lần để xem hình ảnh" if img_data and not isinstance(img_data, str) else "Không có ảnh"
            if img_data and not isinstance(img_data, str):
                img = ImageManager.blob_to_image(img_data)
                if img:
                    self.image_references.append(img)
            
            self.tree.insert("", "end", values=(
                product[0], product[1], product[2], 
                img_preview,
                f"{product[4]:,.0f}đ", 
                f"{product[5]:,.0f}đ", 
                product[6]
            ))
    
    def show_full_image(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        
        item = self.tree.item(selected[0])
        product_id = item['values'][0]
        
        with sqlite3.connect("quanlybanhang.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT anh_sp FROM sanpham WHERE id=?", (product_id,))
            img_data = cursor.fetchone()[0]
        
        if not img_data or isinstance(img_data, str):
            messagebox.showinfo("Thông báo", "Sản phẩm không có ảnh!")
            return
        
        img_window = tk.Toplevel(self.root)
        img_window.title("Xem ảnh sản phẩm")
        
        img = Image.open(BytesIO(img_data))
        photo = ImageTk.PhotoImage(img)
        
        tk.Label(img_window, image=photo).pack()
        img_window.image = photo
    
    def add_product_dialog(self):
        self.dialog = tk.Toplevel(self.root)
        self.dialog.title("Thêm sản phẩm mới")
        self.dialog.grab_set()
        
        self.ma_sp = tk.StringVar()
        self.ten_sp = tk.StringVar()
        self.gia_nhap = tk.DoubleVar(value=0.0)
        self.gia_ban = tk.DoubleVar(value=0.0)
        self.so_luong = tk.IntVar(value=0)
        self.anh_path = tk.StringVar()
        self.image_preview = None
        
        tk.Label(self.dialog, text="Mã sản phẩm:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        tk.Entry(self.dialog, textvariable=self.ma_sp).grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(self.dialog, text="Tên sản phẩm:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        tk.Entry(self.dialog, textvariable=self.ten_sp).grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(self.dialog, text="Giá nhập:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        tk.Entry(self.dialog, textvariable=self.gia_nhap).grid(row=2, column=1, padx=5, pady=5)
        
        tk.Label(self.dialog, text="Giá bán:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        tk.Entry(self.dialog, textvariable=self.gia_ban).grid(row=3, column=1, padx=5, pady=5)
        
        tk.Label(self.dialog, text="Số lượng:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        tk.Entry(self.dialog, textvariable=self.so_luong).grid(row=4, column=1, padx=5, pady=5)
        
        tk.Label(self.dialog, text="Ảnh sản phẩm:").grid(row=5, column=0, padx=5, pady=5, sticky="e")
        tk.Entry(self.dialog, textvariable=self.anh_path, state="readonly").grid(row=5, column=1, padx=5, pady=5)
        tk.Button(self.dialog, text="Chọn ảnh", command=self.select_and_preview_image).grid(row=5, column=2, padx=5, pady=5)
        
        self.preview_label = tk.Label(self.dialog)
        self.preview_label.grid(row=6, column=0, columnspan=3, pady=10)
        
        btn_frame = tk.Frame(self.dialog)
        btn_frame.grid(row=7, column=0, columnspan=3, pady=10)
        
        tk.Button(btn_frame, text="Lưu", command=self.save_product).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Hủy", command=self.dialog.destroy).pack(side="left", padx=10)
    
    def select_and_preview_image(self):
        file_path = filedialog.askopenfilename(
            title="Chọn ảnh sản phẩm", 
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp *.gif")]
        )
        if file_path:
            self.anh_path.set(file_path)
            try:
                img = ImageManager.resize_image(file_path, (150, 150))
                if img:
                    self.image_preview = img
                    self.preview_label.config(image=img)
                else:
                    messagebox.showerror("Lỗi", "Không thể mở ảnh!")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể mở ảnh: {str(e)}")
    
    def save_product(self):
        try:
            ma_sp = self.ma_sp.get().strip()
            ten_sp = self.ten_sp.get().strip()
            gia_nhap = self.gia_nhap.get()
            gia_ban = self.gia_ban.get()
            so_luong = self.so_luong.get()
            if not ma_sp or not ten_sp:
                raise ValueError("Mã và tên sản phẩm không được để trống!")
            if gia_nhap < 0 or gia_ban < 0 or so_luong < 0:
                raise ValueError("Giá và số lượng không được âm!")
            
            img_blob = None
            if self.anh_path.get():
                img_blob = ImageManager.image_to_blob(self.anh_path.get())
                if not img_blob:
                    raise ValueError("Không thể xử lý ảnh!")
            
            with sqlite3.connect("quanlybanhang.db") as conn:
                cursor = conn.cursor()
                cursor.execute('''INSERT INTO sanpham 
                               (ma_sp, ten_sp, anh_sp, gia_nhap, gia_ban, so_luong)
                               VALUES (?, ?, ?, ?, ?, ?)''',
                               (ma_sp, ten_sp, img_blob, gia_nhap, gia_ban, so_luong))
                conn.commit()
            
            self.dialog.destroy()
            self.load_products()
        
        except tk.TclError:
            messagebox.showerror("Lỗi", "Vui lòng nhập số hợp lệ cho giá và số lượng!")
        except sqlite3.IntegrityError:
            messagebox.showerror("Lỗi", "Mã sản phẩm đã tồn tại!")
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e))
        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {str(e)}")
    
    def edit_product(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn sản phẩm cần sửa!")
            return
        
        product_id = self.tree.item(selected[0])['values'][0]
        with sqlite3.connect("quanlybanhang.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sanpham WHERE id=?", (product_id,))
            product = cursor.fetchone()
        
        if not product:
            messagebox.showerror("Lỗi", "Không tìm thấy sản phẩm!")
            return
        
        self.dialog = tk.Toplevel(self.root)
        self.dialog.title("Chỉnh sửa sản phẩm")
        self.dialog.grab_set()
        
        self.edit_id = product_id
        self.ma_sp = tk.StringVar(value=product[1])
        self.ten_sp = tk.StringVar(value=product[2])
        self.gia_nhap = tk.DoubleVar(value=product[4])
        self.gia_ban = tk.DoubleVar(value=product[5])
        self.so_luong = tk.IntVar(value=product[6])
        self.anh_blob = product[3]
        self.anh_path = tk.StringVar()
        self.image_preview = None
        
        tk.Label(self.dialog, text="Mã sản phẩm:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        tk.Entry(self.dialog, textvariable=self.ma_sp).grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(self.dialog, text="Tên sản phẩm:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        tk.Entry(self.dialog, textvariable=self.ten_sp).grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(self.dialog, text="Giá nhập:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        tk.Entry(self.dialog, textvariable=self.gia_nhap).grid(row=2, column=1, padx=5, pady=5)
        
        tk.Label(self.dialog, text="Giá bán:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        tk.Entry(self.dialog, textvariable=self.gia_ban).grid(row=3, column=1, padx=5, pady=5)
        
        tk.Label(self.dialog, text="Số lượng:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        tk.Entry(self.dialog, textvariable=self.so_luong).grid(row=4, column=1, padx=5, pady=5)
        
        tk.Label(self.dialog, text="Ảnh sản phẩm:").grid(row=5, column=0, padx=5, pady=5, sticky="e")
        tk.Entry(self.dialog, textvariable=self.anh_path, state="readonly").grid(row=5, column=1, padx=5, pady=5)
        tk.Button(self.dialog, text="Chọn ảnh", command=self.select_and_preview_image).grid(row=5, column=2, padx=5, pady=5)
        
        self.preview_label = tk.Label(self.dialog)
        self.preview_label.grid(row=6, column=0, columnspan=3, pady=10)
        if self.anh_blob and not isinstance(self.anh_blob, str):
            img = ImageManager.blob_to_image(self.anh_blob)
            if img:
                self.image_preview = img
                self.preview_label.config(image=img)
        
        btn_frame = tk.Frame(self.dialog)
        btn_frame.grid(row=7, column=0, columnspan=3, pady=10)
        
        tk.Button(btn_frame, text="Cập nhật", command=self.update_product).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Hủy", command=self.dialog.destroy).pack(side="left", padx=10)
    
    def update_product(self):
        try:
            ma_sp = self.ma_sp.get().strip()
            ten_sp = self.ten_sp.get().strip()
            gia_nhap = self.gia_nhap.get()
            gia_ban = self.gia_ban.get()
            so_luong = self.so_luong.get()
            if not ma_sp or not ten_sp:
                raise ValueError("Mã và tên sản phẩm không được để trống!")
            if gia_nhap < 0 or gia_ban < 0 or so_luong < 0:
                raise ValueError("Giá và số lượng không được âm!")
            
            img_blob = self.anh_blob
            if self.anh_path.get():
                img_blob = ImageManager.image_to_blob(self.anh_path.get())
                if not img_blob:
                    raise ValueError("Không thể xử lý ảnh!")
            
            with sqlite3.connect("quanlybanhang.db") as conn:
                cursor = conn.cursor()
                cursor.execute('''UPDATE sanpham SET
                               ma_sp=?, ten_sp=?, anh_sp=?, gia_nhap=?, gia_ban=?, so_luong=?
                               WHERE id=?''',
                               (ma_sp, ten_sp, img_blob, gia_nhap, gia_ban, so_luong, self.edit_id))
                conn.commit()
            
            self.dialog.destroy()
            self.load_products()
        
        except tk.TclError:
            messagebox.showerror("Lỗi", "Vui lòng nhập số hợp lệ!")
        except sqlite3.IntegrityError:
            messagebox.showerror("Lỗi", "Mã sản phẩm đã tồn tại!")
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e))
        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {str(e)}")
    
    def delete_product(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn sản phẩm cần xóa!")
            return
        
        product_id = self.tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa sản phẩm này?"):
            try:
                with sqlite3.connect("quanlybanhang.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM sanpham WHERE id=?", (product_id,))
                    conn.commit()
                
                self.load_products()
            except sqlite3.Error as e:
                messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {str(e)}")

class OrderManager:
    def __init__(self, root):
        self.root = root
        self.setup_ui()
        self.load_orders()
    
    def setup_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        tk.Label(main_frame, text="QUẢN LÝ ĐƠN HÀNG", font=("Arial", 18, "bold")).pack(pady=10)
        
        toolbar = tk.Frame(main_frame)
        toolbar.pack(fill="x", pady=10)
        
        tk.Button(toolbar, text="Thêm đơn hàng", command=self.add_order_dialog).pack(side="left", padx=5)
        tk.Button(toolbar, text="Cập nhật trạng thái", command=self.update_status).pack(side="left", padx=5)
        tk.Button(toolbar, text="Xóa đơn hàng", command=self.delete_order).pack(side="left", padx=5)
        tk.Button(toolbar, text="Quay lại", command=lambda: MainApp(self.root)).pack(side="right", padx=5)
        
        # Thêm ô tìm kiếm
        tk.Label(toolbar, text="Tìm kiếm:").pack(side="left", padx=5)
        self.search_var = tk.StringVar()
        tk.Entry(toolbar, textvariable=self.search_var).pack(side="left", padx=5)
        tk.Button(toolbar, text="Tìm", command=self.search_orders).pack(side="left", padx=5)
        tk.Button(toolbar, text="Hủy tìm kiếm", command=self.load_orders).pack(side="left", padx=5)
        
        columns = ("ID", "Tên KH", "Danh mục", "Ngày đặt", "Ngày giao", "File SP",
                   "Tổng tiền", "Đã cọc", "Còn thiếu", "Trạng thái")
        self.tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=20)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100 if col not in ["Tên KH", "Danh mục", "File SP"] else 150)
        
        self.tree.pack(fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(self.tree, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)
    
    def load_orders(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        with sqlite3.connect("quanlybanhang.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, ten_kh, danh_muc, ngay_dat, ngay_giao, file_sp, "
                          "tong_tien, da_coc, con_thieu, trang_thai FROM khachhang")
            orders = cursor.fetchall()
        
        for order in orders:
            self.tree.insert("", "end", values=(
                order[0], order[1], order[2], order[3], order[4], order[5],
                f"{order[6]:,.0f}đ", f"{order[7]:,.0f}đ", f"{order[8]:,.0f}đ", order[9]
            ))
    
    def search_orders(self):
        query = self.search_var.get().strip().lower()
        if not query:
            self.load_orders()
            return
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        with sqlite3.connect("quanlybanhang.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, ten_kh, danh_muc, ngay_dat, ngay_giao, file_sp, "
                          "tong_tien, da_coc, con_thieu, trang_thai FROM khachhang "
                          "WHERE LOWER(ten_kh) LIKE ? OR LOWER(danh_muc) LIKE ?",
                          (f"%{query}%", f"%{query}%"))
            orders = cursor.fetchall()
        
        for order in orders:
            self.tree.insert("", "end", values=(
                order[0], order[1], order[2], order[3], order[4], order[5],
                f"{order[6]:,.0f}đ", f"{order[7]:,.0f}đ", f"{order[8]:,.0f}đ", order[9]
            ))
    
    def add_order_dialog(self):
        self.dialog = tk.Toplevel(self.root)
        self.dialog.title("Thêm đơn hàng mới")
        self.dialog.grab_set()
        
        self.ten_kh = tk.StringVar()
        self.danh_muc = tk.StringVar()
        self.ngay_dat = tk.StringVar()
        self.ngay_giao = tk.StringVar()
        self.file_sp = tk.StringVar()
        self.tong_tien = tk.DoubleVar(value=0.0)
        self.da_coc = tk.DoubleVar(value=0.0)
        self.trang_thai = tk.StringVar(value="đang đặt")
        
        tk.Label(self.dialog, text="Tên khách hàng:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        tk.Entry(self.dialog, textvariable=self.ten_kh).grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(self.dialog, text="Danh mục hàng:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        tk.Entry(self.dialog, textvariable=self.danh_muc).grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(self.dialog, text="Ngày đặt hàng:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        DateEntry(self.dialog, textvariable=self.ngay_dat, date_pattern='dd/mm/yyyy').grid(row=2, column=1, padx=5, pady=5)
        
        tk.Label(self.dialog, text="Ngày giao hàng:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        DateEntry(self.dialog, textvariable=self.ngay_giao, date_pattern='dd/mm/yyyy').grid(row=3, column=1, padx=5, pady=5)
        
        tk.Label(self.dialog, text="File sản phẩm:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        tk.Entry(self.dialog, textvariable=self.file_sp, state="readonly").grid(row=4, column=1, padx=5, pady=5)
        tk.Button(self.dialog, text="Chọn file", command=self.select_file).grid(row=4, column=2, padx=5, pady=5)
        
        tk.Label(self.dialog, text="Tổng tiền:").grid(row=5, column=0, padx=5, pady=5, sticky="e")
        tk.Entry(self.dialog, textvariable=self.tong_tien).grid(row=5, column=1, padx=5, pady=5)
        
        tk.Label(self.dialog, text="Đã cọc:").grid(row=6, column=0, padx=5, pady=5, sticky="e")
        tk.Entry(self.dialog, textvariable=self.da_coc).grid(row=6, column=1, padx=5, pady=5)
        
        tk.Label(self.dialog, text="Trạng thái:").grid(row=7, column=0, padx=5, pady=5, sticky="e")
        ttk.Combobox(self.dialog, textvariable=self.trang_thai,
                     values=["đang đặt", "đã về", "đã giao"], state="readonly").grid(row=7, column=1, padx=5, pady=5)
        
        btn_frame = tk.Frame(self.dialog)
        btn_frame.grid(row=8, column=0, columnspan=3, pady=10)
        
        tk.Button(btn_frame, text="Lưu", command=self.save_order).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Hủy", command=self.dialog.destroy).pack(side="left", padx=10)
    
    def select_file(self):
        file_path = filedialog.askopenfilename(title="Chọn file sản phẩm")
        if file_path:
            self.file_sp.set(file_path)
    
    def save_order(self):
        try:
            ten_kh = self.ten_kh.get().strip()
            danh_muc = self.danh_muc.get().strip()
            ngay_dat = self.ngay_dat.get()
            ngay_giao = self.ngay_giao.get()
            tong_tien = self.tong_tien.get()
            da_coc = self.da_coc.get()
            
            if not ten_kh or not danh_muc or not ngay_dat:
                raise ValueError("Vui lòng nhập đầy đủ thông tin bắt buộc!")
            if tong_tien < 0 or da_coc < 0:
                raise ValueError("Tiền không được âm!")
            if da_coc > tong_tien:
                raise ValueError("Số tiền cọc không được lớn hơn tổng tiền!")
            if ngay_giao:
                date_format = "%d/%m/%Y"
                if datetime.strptime(ngay_giao, date_format) < datetime.strptime(ngay_dat, date_format):
                    raise ValueError("Ngày giao phải sau ngày đặt!")
            
            with sqlite3.connect("quanlybanhang.db") as conn:
                cursor = conn.cursor()
                cursor.execute('''INSERT INTO khachhang
                               (ten_kh, danh_muc, ngay_dat, ngay_giao, file_sp, tong_tien, da_coc, trang_thai)
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                               (ten_kh, danh_muc, ngay_dat, ngay_giao, self.file_sp.get(), 
                                tong_tien, da_coc, self.trang_thai.get()))
                conn.commit()
            
            self.dialog.destroy()
            self.load_orders()
        
        except tk.TclError:
            messagebox.showerror("Lỗi", "Vui lòng nhập số tiền hợp lệ!")
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e))
        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {str(e)}")
    
    def update_status(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn đơn hàng cần cập nhật!")
            return
        
        order_id = self.tree.item(selected[0])['values'][0]
        current_status = self.tree.item(selected[0])['values'][9]
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Cập nhật trạng thái đơn hàng")
        dialog.grab_set()
        
        tk.Label(dialog, text="Trạng thái mới:").pack(pady=5)
        status_var = tk.StringVar(value=current_status)
        ttk.Combobox(dialog, textvariable=status_var,
                     values=["đang đặt", "đã về", "đã giao"], state="readonly").pack(pady=5)
        
        def do_update():
            new_status = status_var.get()
            if new_status == current_status:
                dialog.destroy()
                return
            
            try:
                with sqlite3.connect("quanlybanhang.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE khachhang SET trang_thai=? WHERE id=?", (new_status, order_id))
                    conn.commit()
                
                dialog.destroy()
                self.load_orders()
            except sqlite3.Error as e:
                messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {str(e)}")
        
        tk.Button(dialog, text="Cập nhật", command=do_update).pack(pady=10)
        tk.Button(dialog, text="Hủy", command=dialog.destroy).pack(pady=5)
    
    def delete_order(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn đơn hàng cần xóa!")
            return
        
        order_id = self.tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa đơn hàng này?"):
            try:
                with sqlite3.connect("quanlybanhang.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM khachhang WHERE id=?", (order_id,))
                    conn.commit()
                messagebox.showinfo("Thành công", "Xóa đơn hàng thành công!")
                self.load_orders()
            except sqlite3.Error as e:
                messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()