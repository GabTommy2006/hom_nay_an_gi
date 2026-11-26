from pathlib import Path
import re, html, textwrap, subprocess, zipfile, hashlib, json
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
MD=OUT/'Bao_cao_Hom_nay_an_gi.md'
pdfmetrics.registerFont(TTFont('ArialVN',r'C:\Windows\Fonts\arial.ttf'))
pdfmetrics.registerFont(TTFont('ArialVNB',r'C:\Windows\Fonts\arialbd.ttf'))
pdfmetrics.registerFont(TTFont('ConsolasVN',r'C:\Windows\Fonts\consola.ttf'))
pdfmetrics.registerFontFamily('ArialVN',normal='ArialVN',bold='ArialVNB',italic='ArialVN',boldItalic='ArialVNB')

snips=[
 ('A Điểm vào Vercel','api/index.js',1,1,'Function dùng lại handleRequest của server local để tránh tạo hai bộ phân quyền khác nhau.'),
 ('B Phân luồng HTTP','server/app.js',17,30,'Auth và admin được xử lý trước các API công khai. Endpoint API lạ trả 404; yêu cầu file tĩnh chỉ hỗ trợ GET và HEAD.'),
 ('C Sinh dữ liệu frontend từ MySQL','server/app.js',38,48,'FOOD và RECIPES giữ nguyên hợp đồng frontend, nhưng nội dung lấy từ Model MySQL; dữ liệu trả về không được cache thành bản seed cũ.'),
 ('D Pool MySQL và giải phóng kết nối','server/config/database.js',16,30,'Pool dùng lại trong instance. maxIdle nhỏ hơn connectionLimit kích hoạt dọn kết nối rảnh của mysql2. rows truyền tham số tách khỏi SQL.'),
 ('E Kiểm tra admin phía server','server/middleware/auth.js',5,19,'Phiên được Better Auth xác minh; role được đọc lại từ users. API trả 401 hoặc 403; trang HTML điều hướng về đăng nhập.'),
 ('F Chọn món trong tập đã lọc','public/js/app.js',25,37,'Hàm chọn món dùng sessionStorage để giảm lặp và ưu tiên bữa hiện tại. Tập pool do bộ lọc cung cấp, không tự đưa món ngoài tập vào.'),
 ('G Áp dụng tùy chọn quay','public/js/spin-filters.js',3,11,'Whitelist diet và điều kiện recipe/linked được dùng chung cho số lượng món và lượt quay.'),
 ('H Tính định lượng nguyên liệu','public/js/recipe.js',65,73,'Lượng mới bằng lượng gốc nhân số người mới chia khẩu phần gốc. Khoảng số được tính từng đầu mút; văn bản giữ nguyên.'),
 ('I Kiểm tra phiên bản khi ghi quán','server/models/admin-restaurant.model.js',6,20,'Một connection duy nhất được giữ cho transaction. Khóa bản ghi và revision chống ghi đè; requestId hỗ trợ xử lý lần ghi lặp.'),
 ('I2 Lưu liên kết và kết thúc transaction','server/models/admin-restaurant.model.js',30,40,'Sau phần INSERT hoặc UPDATE bản chính, Model ghi trạng thái hiển thị, bữa và audit, rồi commit. Lỗi dẫn tới rollback; finally luôn release connection.'),
 ('J Kiểm soát JSON và Origin','server/utils/http.js',1,12,'Không tin dữ liệu từ trình duyệt: giới hạn kích thước, kiểm tra Origin, loại nội dung và cấu trúc JSON trước khi ghi.'),
 ('K Cấu hình Vercel','vercel.json',1,18,'Toàn bộ route đi qua Function. includeFiles đóng gói public cho bộ phục vụ tĩnh có kiểm soát; build không nhập dữ liệu.'),
]
base=MD.read_text(encoding='utf-8').split('\n### A Điểm vào Vercel')[0]
for title,filename,start,end,explanation in snips:
 lines=(ROOT/filename).read_text(encoding='utf-8').splitlines()
 end=min(end,len(lines))
 base+=f'\n### {title}\n\nFile {filename}, dòng {start} đến {end}. {explanation}\n\n```'+('json' if filename.endswith('.json') else 'javascript')+'\n'+'\n'.join(lines[start-1:end])+'\n```\n'
MD.write_text(base,encoding='utf-8')

styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='BodyVN',fontName='ArialVN',fontSize=10.3,leading=15.2,spaceAfter=7.2,textColor=colors.HexColor('#26323c'),splitLongWords=True))
styles.add(ParagraphStyle(name='TitleVN',fontName='ArialVNB',fontSize=26,leading=33,spaceAfter=19,textColor=colors.black))
styles.add(ParagraphStyle(name='H1VN',fontName='ArialVNB',fontSize=16,leading=21,spaceBefore=17,spaceAfter=9,keepWithNext=True,textColor=colors.HexColor('#173d47')))
styles.add(ParagraphStyle(name='H2VN',fontName='ArialVNB',fontSize=12.2,leading=17,spaceBefore=10,spaceAfter=6,keepWithNext=True,textColor=colors.HexColor('#173d47')))
styles.add(ParagraphStyle(name='BulletVN',parent=styles['BodyVN'],leftIndent=12,firstLineIndent=-9,spaceAfter=5))
styles.add(ParagraphStyle(name='CodeVN',fontName='ConsolasVN',fontSize=7.2,leading=9.2,spaceBefore=5,spaceAfter=10,backColor=colors.HexColor('#f0f3f4'),borderPadding=7))
styles.add(ParagraphStyle(name='CaptionVN',parent=styles['BodyVN'],fontSize=9,textColor=colors.HexColor('#65717a'),spaceBefore=5))

def fmt(s):
 s=html.escape(s)
 s=re.sub(r'`([^`]+)`',r'<font name="ConsolasVN">\1</font>',s)
 s=re.sub(r'(https?://[^\s<]+)',r'<link href="\1" color="#166273">\1</link>',s)
 return s

class ReportDoc(SimpleDocTemplate):
 def afterFlowable(self,f):
  if isinstance(f,Paragraph) and f.style.name in ('H1VN','H2VN'):
   name='heading-'+str(self.seq.nextf('headings'))
   self.canv.bookmarkPage(name)
   self.canv.addOutlineEntry(f.getPlainText(),name,0 if f.style.name=='H1VN' else 1,False)

def diagram():
 d=Drawing(477,112)
 labels=[('Trình duyệt','HTML CSS JS'),('Node trên Vercel','Route Controller'),('Model và mysql2','Pool Transaction'),('MySQL Aiven','Dữ liệu và phiên')]
 for i,(a,b) in enumerate(labels):
  x=i*121
  d.add(Rect(x,42,110,56,rx=5,ry=5,fillColor=colors.HexColor('#edf3f4'),strokeColor=colors.HexColor('#b5c9cc')))
  d.add(String(x+55,77,a,fontName='ArialVNB',fontSize=9,textAnchor='middle',fillColor=colors.HexColor('#173d47')))
  d.add(String(x+55,59,b,fontName='ArialVN',fontSize=8,textAnchor='middle'))
  if i<3:
   d.add(Line(x+111,70,x+120,70,strokeColor=colors.HexColor('#3e7f86')))
   d.add(Polygon([x+117,73,x+121,70,x+117,67],fillColor=colors.HexColor('#3e7f86'),strokeColor=None))
 d.add(String(0,16,'Dữ liệu trả về theo chiều ngược lại để cập nhật giao diện',fontName='ArialVN',fontSize=9,fillColor=colors.HexColor('#65717a')))
 return d

flow=[]
paragraph=[]
in_code=False;code=[]
def flush():
 if paragraph:
  flow.append(Paragraph(fmt(' '.join(paragraph)),styles['BodyVN']));paragraph.clear()
for line in base.splitlines():
 if line.startswith('```'):
  flush()
  if not in_code:in_code=True;code=[]
  else:
   expanded=[]
   for ln in code:
    expanded.extend(textwrap.wrap(ln,98,subsequent_indent='    ',replace_whitespace=False,drop_whitespace=False) or [''])
   flow.append(Preformatted('\n'.join(expanded),styles['CodeVN']));in_code=False
  continue
 if in_code:code.append(line);continue
 if not line.strip():flush();continue
 if line.startswith('# '):
  flush();flow.append(Paragraph('Báo cáo xây dựng website<br/>Hôm nay ăn gì',styles['TitleVN']));continue
 if line.startswith('## '):
  flush();flow.append(Paragraph(fmt(line[3:]),styles['H1VN']));continue
 if line.startswith('### '):
  flush();flow.append(Paragraph(fmt(line[4:]),styles['H2VN']))
  if line.startswith('### 2.2'):flow.append(diagram())
  continue
 if line.startswith('- '):
  flush();flow.append(Paragraph('• '+fmt(line[2:]),styles['BulletVN']));continue
 paragraph.append(line)
flush()

def page(canvas,doc):
 canvas.saveState();canvas.setFont('ArialVN',8);canvas.setFillColor(colors.HexColor('#6b737a'))
 canvas.drawString(48,27,'Hôm nay ăn gì · Báo cáo kỹ thuật · 07/11/2026')
 canvas.drawRightString(A4[0]-48,27,str(doc.page));canvas.restoreState()

pdf=OUT/'Bao_cao_Hom_nay_an_gi.pdf'
doc=ReportDoc(str(pdf),pagesize=A4,rightMargin=48,leftMargin=48,topMargin=43,bottomMargin=45,title='Báo cáo xây dựng website Hôm nay ăn gì',author='Nhóm 3',pageCompression=1)
doc.build(flow,onFirstPage=page,onLaterPages=page)

files=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')
files=[f for f in files if f and (not f.startswith('.env') or f=='.env.example') and not f.startswith(('output/','.git/','node_modules/')) and (ROOT/f).is_file()]
if (OUT/'Ma_nguon_Hom_nay_an_gi_87a232a.zip').exists():
 print(json.dumps({'pdf':str(pdf),'sourceFiles':len(files),'sourceArchive':'existing verified snapshot'},ensure_ascii=False))
 raise SystemExit(0)
manifest=[]
with zipfile.ZipFile(OUT/'Ma_nguon_Hom_nay_an_gi_87a232a.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in files:
  raw=(ROOT/f).read_bytes();manifest.append(hashlib.sha256(raw).hexdigest()+'  '+f);z.writestr('hom_nay_an_gi/'+f,raw)
 z.writestr('hom_nay_an_gi/MANIFEST-SHA256.txt','\n'.join(manifest))
 z.writestr('hom_nay_an_gi/PHIEN_BAN_BAO_CAO.txt','Commit 87a232a72fac849a36d117ff714a61882ec32f1e\nBranch Update-web-6.0\nBao cao 07/11/2026\nKhong kem .env that, node_modules, backup database hay lich su Git.\nChay npm ci va tu cau hinh .env theo README.\n')
print(json.dumps({'pdf':str(pdf),'sourceFiles':len(files),'pdfBytes':pdf.stat().st_size},ensure_ascii=False))
