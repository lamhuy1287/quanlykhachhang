import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
import sqlite3
from PIL import Image, ImageTk
import os


def init_db():
    """Khởi tạo cơ sở dữ liệu SQLite với bảng sanpham và khachhang."""
    conn = sqlite3.connect("quanlybanhang.db")
    cursor = conn.cursor()

    # Bảng sản phẩm
    cursor.execute('''CREATE TABLE IF NOT EXISTS sanpham (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ma_sp TEXT UNIQUE,
                    ten_sp TEXT,
                    anh_sp TEXT,
                    gia_nhap REAL,
                    gia_ban REAL,
                    so_luong INTEGER)''')

    # Bảng khách hàng
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
    conn.close()


init_db()


class MainApp:
    """Lớp chính quản lý giao diện menu của ứng dụng."""
    def __init__(self, root):
        self.root = root
        self.root.title("HỆ THỐNG QUẢN LÝ BÁN HÀNG")
        self.root.geometry("1280x720")
        self.root.state('zoomed')

        self.setup_main_frame()

    def setup_main_frame(self):
        """Thiết lập giao diện chính với các nút chức năng."""
        # Xóa các widget cũ
        for widget in self.root.winfo_children():
            widget.destroy()

        # Frame chính
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill="both", expand=True)

        # Tiêu đề
        tk.Label(main_frame, text="HỆ THỐNG QUẢN LÝ BÁN HÀNG",
                 font=("Arial", 24, "bold"), bg="#f0f0f0", fg="#2c3e50").pack(pady=50)

        # Nút chức năng
        btn_frame = tk.Frame(main_frame, bg="#f0f0f0")
        btn_frame.pack(pady=50)

        tk.Button(btn_frame, text="QUẢN LÝ SẢN PHẨM", width=25, height=3,
                  font=("Arial", 14), command=self.open_product_manager,
                  bg="#3498db", fg="black").grid(row=0, column=0, padx=20)

        tk.Button(btn_frame, text="QUẢN LÝ ĐƠN HÀNG", width=25, height=3,
                  font=("Arial", 14), command=self.open_order_manager,
                  bg="#2ecc71", fg="black").grid(row=0, column=1, padx=20)

        tk.Button(btn_frame, text="THOÁT", width=25, height=3,
                  font=("Arial", 14), command=self.root.quit,
                  bg="#e74c3c", fg="black").grid(row=0, column=2, padx=20)

    def open_product_manager(self):
        """Mở giao diện quản lý sản phẩm."""
        ProductManager(self.root)

    def open_order_manager(self):
        """Mở giao diện quản lý đơn hàng."""
        OrderManager(self.root)


class ProductManager:
    """Lớp quản lý sản phẩm (thêm, sửa, xóa, hiển thị)."""
    def __init__(self, root):
        self.root = root
        self.setup_ui()
        self.load_products()

    def setup_ui(self):
        """Thiết lập giao diện quản lý sản phẩm."""
        # Xóa các widget cũ
        for widget in self.root.winfo_children():
            widget.destroy()

        # Frame chính
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Tiêu đề
        tk.Label(main_frame, text="QUẢN LÝ SẢN PHẨM", font=("Arial", 18, "bold")).pack(pady=10)

        # Thanh công cụ
        toolbar = tk.Frame(main_frame)
        toolbar.pack(fill="x", pady=10)

        tk.Button(toolbar, text="Thêm sản phẩm", command=self.add_product_dialog).pack(side="left", padx=5)
        tk.Button(toolbar, text="Sửa sản phẩm", command=self.edit_product).pack(side="left", padx=5)
        tk.Button(toolbar, text="Xóa sản phẩm", command=self.delete_product).pack(side="left", padx=5)
        tk.Button(toolbar, text="Quay lại", command=lambda: MainApp(self.root)).pack(side="right", padx=5)

        # Bảng sản phẩm
        columns = ("ID", "Mã SP", "Tên SP", "Ảnh", "Giá nhập", "Giá bán", "Số lượng")
        self.tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=20)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120 if col != "Tên SP" else 200)

        self.tree.pack(fill="both", expand=True)

        # Thanh cuộn
        scrollbar = ttk.Scrollbar(self.tree, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

    def load_products(self):
        """Tải danh sách sản phẩm từ CSDL và hiển thị lên Treeview."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        with sqlite3.connect("quanlybanhang.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, ma_sp, ten_sp, anh_sp, gia_nhap, gia_ban, so_luong FROM sanpham")
            products = cursor.fetchall()

        for product in products:
            self.tree.insert("", "end", values=product)

    def add_product_dialog(self):
        """Hiển thị dialog để thêm sản phẩm mới."""
        self.dialog = tk.Toplevel(self.root)
        self.dialog.title("Thêm sản phẩm mới")
        self.dialog.geometry("400x300")
        self.dialog.grab_set()

        # Biến lưu dữ liệu
        self.ma_sp = tk.StringVar()
        self.ten_sp = tk.StringVar()
        self.gia_nhap = tk.DoubleVar(value=0.0)
        self.gia_ban = tk.DoubleVar(value=0.0)
        self.so_luong = tk.IntVar(value=0)
        self.anh_path = tk.StringVar()

        # Form nhập liệu
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
        tk.Button(self.dialog, text="Chọn ảnh", command=self.select_image).grid(row=5, column=2, padx=5, pady=5)

        # Nút lưu và hủy
        btn_frame = tk.Frame(self.dialog)
        btn_frame.grid(row=6, column=0, columnspan=3, pady=10)

        tk.Button(btn_frame, text="Lưu", command=self.save_product).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Hủy", command=self.dialog.destroy).pack(side="left", padx=10)

    def select_image(self):
        """Mở dialog chọn ảnh sản phẩm."""
        file_path = filedialog.askopenfilename(title="Chọn ảnh sản phẩm",
                                              filetypes=[("Image Files", "*.jpg *.jpeg *.png")])
        if file_path:
            self.anh_path.set(file_path)

    def save_product(self):
        """Lưu sản phẩm mới vào CSDL."""
        if not all([self.ma_sp.get(), self.ten_sp.get()]):
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ mã và tên sản phẩm!")
            return

        try:
            if self.gia_nhap.get() < 0 or self.gia_ban.get() < 0 or self.so_luong.get() < 0:
                messagebox.showerror("Lỗi", "Giá và số lượng không được âm!")
                return
        except tk.TclError:
            messagebox.showerror("Lỗi", "Vui lòng nhập giá và số lượng hợp lệ!")
            return

        try:
            with sqlite3.connect("quanlybanhang.db") as conn:
                cursor = conn.cursor()
                cursor.execute('''INSERT INTO sanpham (ma_sp, ten_sp, anh_sp, gia_nhap, gia_ban, so_luong)
                               VALUES (?, ?, ?, ?, ?, ?)''',
                              (self.ma_sp.get(), self.ten_sp.get(), self.anh_path.get(),
                               self.gia_nhap.get(), self.gia_ban.get(), self.so_luong.get()))
                conn.commit()

            messagebox.showinfo("Thành công", "Thêm sản phẩm thành công!")
            self.dialog.destroy()
            self.load_products()

        except sqlite3.IntegrityError:
            messagebox.showerror("Lỗi", "Mã sản phẩm đã tồn tại!")
        except sqlite3.Error as e:
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {str(e)}")

    def edit_product(self):
        """Hiển thị dialog để sửa thông tin sản phẩm."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn sản phẩm cần sửa!")
            return

        product_id = self.tree.item(selected[0])['values'][0]

        try:
            with sqlite3.connect("quanlybanhang.db") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM sanpham WHERE id=?", (product_id,))
                product = cursor.fetchone()
        except sqlite3.Error as e:
            messagebox.showerror("Lỗi", f"Không thể truy vấn sản phẩm: {str(e)}")
            return

        if not product:
            messagebox.showerror("Lỗi", "Không tìm thấy sản phẩm!")
            return

        # Tạo dialog chỉnh sửa
        self.dialog = tk.Toplevel(self.root)
        self.dialog.title("Chỉnh sửa sản phẩm")
        self.dialog.geometry("400x300")
        self.dialog.grab_set()

        # Biến lưu dữ liệu
        self.edit_id = product_id
        self.ma_sp = tk.StringVar(value=product[1])
        self.ten_sp = tk.StringVar(value=product[2])
        self.gia_nhap = tk.DoubleVar(value=product[4])
        self.gia_ban = tk.DoubleVar(value=product[5])
        self.so_luong = tk.IntVar(value=product[6])
        self.anh_path = tk.StringVar(value=product[3])

        # Form nhập liệu
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
        tk.Button(self.dialog, text="Chọn ảnh", command=self.select_image).grid(row=5, column=2, padx=5, pady=5)

        # Nút cập nhật và hủy
        btn_frame = tk.Frame(self.dialog)
        btn_frame.grid(row=6, column=0, columnspan=3, pady=10)

        tk.Button(btn_frame, text="Cập nhật", command=self.update_product).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Hủy", command=self.dialog.destroy).pack(side="left", padx=10)

    def update_product(self):
        """Cập nhật thông tin sản phẩm vào CSDL."""
        if not all([self.ma_sp.get(), self.ten_sp.get()]):
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ mã và tên sản phẩm!")
            return

        try:
            if self.gia_nhap.get() < 0 or self.gia_ban.get() < 0 or self.so_luong.get() < 0:
                messagebox.showerror("Lỗi", "Giá và số lượng không được âm!")
                return
        except tk.TclError:
            messagebox.showerror("Lỗi", "Vui lòng nhập giá và số lượng hợp lệ!")
            return

        try:
            with sqlite3.connect("quanlybanhang.db") as conn:
                cursor = conn.cursor()
                cursor.execute('''UPDATE sanpham SET
                               ma_sp=?, ten_sp=?, anh_sp=?, gia_nhap=?, gia_ban=?, so_luong=?
                               WHERE id=?''',
                              (self.ma_sp.get(), self.ten_sp.get(), self.anh_path.get(),
                               self.gia_nhap.get(), self.gia_ban.get(), self.so_luong.get(),
                               self.edit_id))
                conn.commit()

            messagebox.showinfo("Thành công", "Cập nhật sản phẩm thành công!")
            self.dialog.destroy()
            self.load_products()

        except sqlite3.IntegrityError:
            messagebox.showerror("Lỗi", "Mã sản phẩm đã tồn tại!")
        except sqlite3.Error as e:
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {str(e)}")

    def delete_product(self):
        """Xóa sản phẩm khỏi CSDL."""
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

                messagebox.showinfo("Thành công", "Xóa sản phẩm thành công!")
                self.load_products()

            except sqlite3.Error as e:
                messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {str(e)}")


class OrderManager:
    """Lớp quản lý đơn hàng (thêm, cập nhật trạng thái, xóa, hiển thị)."""
    def __init__(self, root):
        self.root = root
        self.setup_ui()
        self.load_orders()

    def setup_ui(self):
        """Thiết lập giao diện quản lý đơn hàng."""
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
        """Tải danh sách đơn hàng từ CSDL và hiển thị lên Treeview."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        with sqlite3.connect("quanlybanhang.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, ten_kh, danh_muc, ngay_dat, ngay_giao, file_sp, "
                          "tong_tien, da_coc, con_thieu, trang_thai FROM khachhang")
            orders = cursor.fetchall()

        for order in orders:
            self.tree.insert("", "end", values=order)

    def add_order_dialog(self):
        """Hiển thị dialog để thêm đơn hàng mới."""
        self.dialog = tk.Toplevel(self.root)
        self.dialog.title("Thêm đơn hàng mới")
        self.dialog.geometry("600x500")
        self.dialog.grab_set()

        # Biến lưu dữ liệu
        self.ten_kh = tk.StringVar()
        self.danh_muc = tk.StringVar()
        self.ngay_dat = tk.StringVar()
        self.ngay_giao = tk.StringVar()
        self.file_sp = tk.StringVar()
        self.tong_tien = tk.DoubleVar(value=0.0)
        self.da_coc = tk.DoubleVar(value=0.0)
        self.trang_thai = tk.StringVar(value="đang đặt")

        # Form nhập liệu
        tk.Label(self.dialog, text="Tên khách hàng:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        tk.Entry(self.dialog, textvariable=self.ten_kh).grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.dialog, text="Danh mục hàng:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        tk.Entry(self.dialog, textvariable=self.danh_muc).grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self.dialog, text="Ngày đặt hàng:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        DateEntry(self.dialog, textvariable=self.ngay_dat, date_pattern='dd/MM/yyyy').grid(row=2, column=1, padx=5, pady=5)

        tk.Label(self.dialog, text="Ngày giao hàng:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        DateEntry(self.dialog, textvariable=self.ngay_giao, date_pattern='dd/MM/yyyy').grid(row=3, column=1, padx=5, pady=5)

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

        # Nút lưu và hủy
        btn_frame = tk.Frame(self.dialog)
        btn_frame.grid(row=8, column=0, columnspan=3, pady=10)

        tk.Button(btn_frame, text="Lưu", command=self.save_order).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Hủy", command=self.dialog.destroy).pack(side="left", padx=10)

    def select_file(self):
        """Mở dialog chọn file sản phẩm."""
        file_path = filedialog.askopenfilename(title="Chọn file sản phẩm")
        if file_path:
            self.file_sp.set(file_path)

    def save_order(self):
        """Lưu đơn hàng mới vào CSDL."""
        if not all([self.ten_kh.get(), self.danh_muc.get(), self.ngay_dat.get()]):
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin bắt buộc!")
            return

        try:
            if self.tong_tien.get() < 0 or self.da_coc.get() < 0:
                messagebox.showerror("Lỗi", "Tiền không được âm!")
                return
            if self.da_coc.get() > self.tong_tien.get():
                messagebox.showerror("Lỗi", "Số tiền cọc không được lớn hơn tổng tiền!")
                return
        except tk.TclError:
            messagebox.showerror("Lỗi", "Vui lòng nhập số tiền hợp lệ!")
            return

        try:
            with sqlite3.connect("quanlybanhang.db") as conn:
                cursor = conn.cursor()
                cursor.execute('''INSERT INTO khachhang
                               (ten_kh, danh_muc, ngay_dat, ngay_giao, file_sp, tong_tien, da_coc, trang_thai)
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                              (self.ten_kh.get(), self.danh_muc.get(), self.ngay_dat.get(),
                               self.ngay_giao.get(), self.file_sp.get(), self.tong_tien.get(),
                               self.da_coc.get(), self.trang_thai.get()))
                conn.commit()

            messagebox.showinfo("Thành công", "Thêm đơn hàng thành công!")
            self.dialog.destroy()
            self.load_orders()

        except sqlite3.Error as e:
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {str(e)}")

    def update_status(self):
        """Cập nhật trạng thái đơn hàng."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn đơn hàng cần cập nhật!")
            return

        order_id = self.tree.item(selected[0])['values'][0]
        current_status = self.tree.item(selected[0])['values'][9]

        dialog = tk.Toplevel(self.root)
        dialog.title("Cập nhật trạng thái đơn hàng")
        dialog.geometry("300x150")
        dialog.grab_set()

        tk.Label(dialog, text="Trạng thái mới:").pack(pady=5)
        status_var = tk.StringVar(value=current_status)
        status_combo = ttk.Combobox(dialog, textvariable=status_var,
                                    values=["đang đặt", "đã về", "đã giao"], state="readonly")
        status_combo.pack(pady=5)

        def do_update():
            new_status = status_var.get()
            if new_status == current_status:
                messagebox.showinfo("Thông báo", "Trạng thái không thay đổi!")
                dialog.destroy()
                return

            try:
                with sqlite3.connect("quanlybanhang.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE khachhang SET trang_thai=? WHERE id=?", (new_status, order_id))
                    conn.commit()

                messagebox.showinfo("Thành công", "Cập nhật trạng thái thành công!")
                dialog.destroy()
                self.load_orders()

            except sqlite3.Error as e:
                messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {str(e)}")

        tk.Button(dialog, text="Cập nhật", command=do_update).pack(pady=10)
        tk.Button(dialog, text="Hủy", command=dialog.destroy).pack(pady=5)

    def delete_order(self):
        """Xóa đơn hàng khỏi CSDL."""
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