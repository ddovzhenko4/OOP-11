from abc import ABC, abstractmethod
import tkinter as tk
from tkinter import messagebox, ttk

class Telement(ABC):

    def __init__(self, left: "Telement | None" = None, right: "Telement | None" = None):
        self._left = left
        self._right = right

    @abstractmethod
    def result(self) -> float:
        pass

    @abstractmethod
    def copy(self) -> "Telement":
        pass

    @abstractmethod
    def differ(self) -> "Telement":
        pass

    def set_var(self, x: float) -> None:
        if self._left is not None:
            self._left.set_var(x)
        if self._right is not None:
            self._right.set_var(x)

class Real(Telement):

    def __init__(self, f: float):
        super().__init__(None, None)
        self._f = float(f)

    def result(self) -> float:
        return self._f

    def copy(self) -> Telement:
        return Real(self._f)

    def differ(self) -> Telement:
        return Real(0.0)

class Var(Telement):

    def __init__(self, x: float = 0.0):
        super().__init__(None, None)
        self._x = float(x)

    def result(self) -> float:
        return self._x

    def copy(self) -> Telement:
        return Var(self._x)

    def differ(self) -> Telement:
        return Real(1.0)

    def set_var(self, x: float) -> None:
        self._x = float(x)

class Plus(Telement):

    def __init__(self, left: Telement, right: Telement):
        super().__init__(left, right)

    def result(self) -> float:
        return self._left.result() + self._right.result()

    def copy(self) -> Telement:
        return Plus(self._left.copy(), self._right.copy())

    def differ(self) -> Telement:
        return Plus(self._left.differ(), self._right.differ())

class Minus(Telement):

    def __init__(self, left: Telement, right: Telement):
        super().__init__(left, right)

    def result(self) -> float:
        return self._left.result() - self._right.result()

    def copy(self) -> Telement:
        return Minus(self._left.copy(), self._right.copy())

    def differ(self) -> Telement:
        return Minus(self._left.differ(), self._right.differ())

class Mult(Telement):

    def __init__(self, left: Telement, right: Telement):
        super().__init__(left, right)

    def result(self) -> float:
        return self._left.result() * self._right.result()

    def copy(self) -> Telement:
        return Mult(self._left.copy(), self._right.copy())

    def differ(self) -> Telement:
        return Plus(
            Mult(self._left.differ(), self._right.copy()),
            Mult(self._left.copy(), self._right.differ()),
        )

class Div(Telement):

    def __init__(self, left: Telement, right: Telement):
        super().__init__(left, right)

    def result(self) -> float:
        denominator = self._right.result()
        if denominator == 0:
            raise ZeroDivisionError("Ділення на нуль у математичній моделі авто.")
        return self._left.result() / denominator

    def copy(self) -> Telement:
        return Div(self._left.copy(), self._right.copy())

    def differ(self) -> Telement:
        return Div(
            Minus(
                Mult(self._left.differ(), self._right.copy()),
                Mult(self._left.copy(), self._right.differ()),
            ),
            Mult(self._right.copy(), self._right.copy()),
        )


def pos_from_end(s: str, sub: str) -> int:
    return s.rfind(sub)


def form(s: str) -> Telement:
    s = s.replace(" ", "").replace(",", ".")
    if not s:
        raise ValueError("Порожній вираз або некоректний синтаксис.")

    if s.startswith("-"):
        return Minus(Real(0.0), form(s[1:]))

    p = pos_from_end(s, "+")
    if p > 0:
        return Plus(form(s[:p]), form(s[p + 1 :]))

    p = pos_from_end(s, "-")
    if p > 0:
        return Minus(form(s[:p]), form(s[p + 1 :]))

    p = pos_from_end(s, "*")
    if p > 0:
        return Mult(form(s[:p]), form(s[p + 1 :]))

    p = pos_from_end(s, "/")
    if p > 0:
        return Div(form(s[:p]), form(s[p + 1 :]))

    if s.lower() == "x":
        return Var()

    return Real(float(s))

class AutoMatchValuationApp:

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("AutoMatch — Аналіз вартості та амортизації авто")
        self.root.geometry("470x430")
        self.root.resizable(False, False)

        self._build_ui()

    def _build_ui(self) -> None:
        pad = {"padx": 12, "pady": 6}

        model_frame = ttk.LabelFrame(
            self.root, text="Математична модель оцінки авто (AutoMatch)"
        )
        model_frame.pack(fill="x", **pad)

        ttk.Label(model_frame, text="Вік авто x (років):").grid(
            row=0, column=0, sticky="w", padx=8, pady=6
        )
        self.edit_age = ttk.Entry(model_frame, width=32)
        self.edit_age.grid(row=0, column=1, padx=8, pady=6)
        self.edit_age.insert(0, "2+1*2")

        ttk.Label(model_frame, text="Модель ціни f(x), $:").grid(
            row=1, column=0, sticky="w", padx=8, pady=6
        )
        self.edit_formula = ttk.Entry(model_frame, width=32)
        self.edit_formula.grid(row=1, column=1, padx=8, pady=6)
        self.edit_formula.insert(0, "24000-2200*x+120*x*x+800/x")

        res_frame = ttk.LabelFrame(self.root, text="Результати обчислень")
        res_frame.pack(fill="x", **pad)

        labels = [
            ("Вік авто (x), років:", "edit_res_x"),
            ("Ринкова вартість f(x), $:", "edit_res_f"),
            ("Швидкість знецінення f'(x), $/рік:", "edit_res_f1"),
            ("Прискорення зміни f''(x), $/рік²:", "edit_res_f2"),
        ]

        for idx, (text, attr_name) in enumerate(labels):
            ttk.Label(res_frame, text=text).grid(
                row=idx, column=0, sticky="w", padx=8, pady=5
            )
            entry = ttk.Entry(res_frame, width=26, state="readonly")
            entry.grid(row=idx, column=1, padx=8, pady=5)
            setattr(self, attr_name, entry)

        prec_frame = ttk.LabelFrame(self.root, text="Точність")
        prec_frame.pack(fill="x", **pad)

        self.combo_digits = ttk.Combobox(
            prec_frame, values=["0", "1", "2", "3", "4", "5", "6"], width=5, state="readonly"
        )
        self.combo_digits.set("4")
        self.combo_digits.grid(row=0, column=0, padx=8, pady=6)
        self.combo_digits.bind("<<ComboboxSelected>>", lambda _event: self.calculate())

        ttk.Label(prec_frame, text="знаків після десяткової крапки").grid(
            row=0, column=1, sticky="w", padx=4, pady=6
        )

        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Обчислити", width=16, command=self.calculate).grid(
            row=0, column=0, padx=10
        )
        ttk.Button(btn_frame, text="Вихід", width=16, command=self.root.destroy).grid(
            row=0, column=1, padx=10
        )

    def _set_readonly_text(self, entry: ttk.Entry, value: str) -> None:
        entry.config(state="normal")
        entry.delete(0, tk.END)
        entry.insert(0, value)
        entry.config(state="readonly")

    def calculate(self) -> None:
        try:
            x_tree = form(self.edit_age.get())
            f_tree = form(self.edit_formula.get())

            f1_tree = f_tree.differ()
            f2_tree = f1_tree.differ()

            x_val = x_tree.result()

            f_tree.set_var(x_val)
            f1_tree.set_var(x_val)
            f2_tree.set_var(x_val)

            digits = int(self.combo_digits.get())
            fmt = f"{{:.{digits}f}}"

            self._set_readonly_text(self.edit_res_x, fmt.format(x_val))
            self._set_readonly_text(self.edit_res_f, fmt.format(f_tree.result()))
            self._set_readonly_text(self.edit_res_f1, fmt.format(f1_tree.result()))
            self._set_readonly_text(self.edit_res_f2, fmt.format(f2_tree.result()))

        except ZeroDivisionError as err:
            messagebox.showerror("Математична помилка", str(err))
        except Exception as err:
            messagebox.showerror(
                "Помилка введення",
                f"Перевірте правильність виразу (дозволені +, -, *, /, числа та x).\nДеталі: {err}",
            )


if __name__ == "__main__":
    root = tk.Tk()
    app = AutoMatchValuationApp(root)
    root.mainloop()