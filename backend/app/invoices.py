"""Invoice PDFs.

A small, dependency-free PDF writer: we control the layout, there is nothing to
install, and the output is a plain PDF 1.4 file any viewer can open.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field

PAGE_W, PAGE_H = 595, 842          # A4 in points
MARGIN = 48


def _esc(text: str) -> str:
    return (text.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")
            .replace("\r", "").replace("\n", " "))


def _money(paise: int) -> str:
    rupees = paise / 100
    s = f"{rupees:,.2f}"
    # Indian grouping: 1,23,456.78
    whole, _, frac = s.partition(".")
    if len(whole.replace(",", "")) > 3:
        digits = whole.replace(",", "")
        head, tail = digits[:-3], digits[-3:]
        parts = []
        while len(head) > 2:
            parts.insert(0, head[-2:])
            head = head[:-2]
        if head:
            parts.insert(0, head)
        whole = ",".join(parts + [tail])
    return f"Rs. {whole}.{frac}"


@dataclass
class InvoiceLine:
    description: str
    amount_paise: int


@dataclass
class InvoiceDoc:
    number: str
    issued_on: dt.date
    customer_name: str
    customer_phone: str
    professional_name: str
    professional_designation: str
    booking_reference: str
    care_type: str
    shift: str
    days: int
    lines: list[InvoiceLine] = field(default_factory=list)
    gst_paise: int = 0
    notes: str = "NURZING is a nursing bureau and placement service."

    @property
    def subtotal_paise(self) -> int:
        return sum(l.amount_paise for l in self.lines)

    @property
    def total_paise(self) -> int:
        return self.subtotal_paise + self.gst_paise


def _content_stream(doc: InvoiceDoc) -> bytes:
    out: list[str] = []
    y = PAGE_H - MARGIN

    def text(x: float, yy: float, s: str, size: int = 11, bold: bool = False) -> None:
        font = "/F2" if bold else "/F1"
        out.append(f"BT {font} {size} Tf 1 0 0 1 {x:.1f} {yy:.1f} Tm ({_esc(s)}) Tj ET")

    def rule(yy: float) -> None:
        out.append(f"0.75 w 0.6 G {MARGIN} {yy:.1f} m {PAGE_W - MARGIN} {yy:.1f} l S")

    text(MARGIN, y, "NURZING", 22, True)
    text(MARGIN, y - 16, "Nursing bureau and placement service", 9)
    text(PAGE_W - MARGIN - 150, y, "INVOICE", 16, True)
    text(PAGE_W - MARGIN - 150, y - 16, doc.number, 10)
    text(PAGE_W - MARGIN - 150, y - 30, f"Issued {doc.issued_on.isoformat()}", 9)
    y -= 60
    rule(y)
    y -= 26

    text(MARGIN, y, "Billed to", 9, True)
    text(MARGIN, y - 14, doc.customer_name or "Customer", 11)
    text(MARGIN, y - 28, doc.customer_phone, 10)

    text(PAGE_W / 2, y, "Care professional", 9, True)
    text(PAGE_W / 2, y - 14, doc.professional_name, 11)
    text(PAGE_W / 2, y - 28, doc.professional_designation, 10)
    y -= 56
    rule(y)
    y -= 24

    text(MARGIN, y, f"Booking {doc.booking_reference}", 10, True)
    text(MARGIN, y - 14, f"{doc.care_type}  |  {doc.shift}  |  {doc.days} day(s)", 10)
    y -= 44

    text(MARGIN, y, "Description", 9, True)
    text(PAGE_W - MARGIN - 110, y, "Amount", 9, True)
    y -= 8
    rule(y)
    y -= 20

    for line in doc.lines:
        text(MARGIN, y, line.description[:70], 10)
        amt = _money(line.amount_paise)
        text(PAGE_W - MARGIN - 110, y, amt, 10)
        y -= 18

    y -= 6
    rule(y)
    y -= 22
    text(PAGE_W - MARGIN - 200, y, "Subtotal", 10)
    text(PAGE_W - MARGIN - 110, y, _money(doc.subtotal_paise), 10)
    y -= 18
    text(PAGE_W - MARGIN - 200, y, "GST", 10)
    text(PAGE_W - MARGIN - 110, y, _money(doc.gst_paise), 10)
    y -= 24
    text(PAGE_W - MARGIN - 200, y, "Total", 12, True)
    text(PAGE_W - MARGIN - 110, y, _money(doc.total_paise), 12, True)
    y -= 44

    for chunk in _wrap(doc.notes, 92):
        text(MARGIN, y, chunk, 8)
        y -= 12

    return ("\n".join(out) + "\n").encode("latin-1", "replace")


def _wrap(text: str, width: int) -> list[str]:
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    return lines


def render_pdf(doc: InvoiceDoc) -> bytes:
    """Build a valid single-page PDF."""
    stream = _content_stream(doc)
    objects: list[bytes] = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {PAGE_W} {PAGE_H}] "
         f"/Contents 4 0 R /Resources << /Font << /F1 5 0 R /F2 6 0 R >> >> >>").encode(),
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"endstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>",
    ]

    out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for i, obj in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{i} 0 obj\n".encode() + obj + b"\nendobj\n"

    xref_at = len(out)
    out += f"xref\n0 {len(objects) + 1}\n".encode()
    out += b"0000000000 65535 f \n"
    for off in offsets[1:]:
        out += f"{off:010d} 00000 n \n".encode()
    out += (f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_at}\n%%EOF\n").encode()
    return bytes(out)


def invoice_number(booking_reference: str, when: dt.date | None = None) -> str:
    when = when or dt.date.today()
    return f"NZ/{when:%Y%m}/{booking_reference}"
