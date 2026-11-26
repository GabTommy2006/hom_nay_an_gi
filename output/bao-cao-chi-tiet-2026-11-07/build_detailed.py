from pathlib import Path
import json,re,html,textwrap,hashlib,zipfile
from collections import defaultdict
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,Preformatted,Table,TableStyle,Image,KeepTogether
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing,Rect,String,Line,Polygon,Ellipse
from PIL import Image as PILImage

OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
pdfmetrics.registerFont(TTFont('VN',r'C:\Windows\Fonts\arial.ttf'))
pdfmetrics.registerFont(TTFont('VNB',r'C:\Windows\Fonts\arialbd.ttf'))
pdfmetrics.registerFont(TTFont('Code',r'C:\Windows\Fonts\consola.ttf'))
pdfmetrics.registerFontFamily('VN',normal='VN',bold='VNB',italic='VN',boldItalic='VNB')
INK=colors.HexColor('#23343f');ACC=colors.HexColor('#185466');PALE=colors.HexColor('#eef4f5')
S={
 'body':ParagraphStyle('body',fontName='VN',fontSize=10.2,leading=15,spaceAfter=7,textColor=INK),
 'h1':ParagraphStyle('h1',fontName='VNB',fontSize=17,leading=22,spaceBefore=15,spaceAfter=10,keepWithNext=True,textColor=ACC),
 'h2':ParagraphStyle('h2',fontName='VNB',fontSize=12.2,leading=17,spaceBefore=11,spaceAfter=6,keepWithNext=True,textColor=ACC),
 'caption':ParagraphStyle('caption',fontName='VN',fontSize=8.8,leading=12,spaceBefore=4,spaceAfter=9,textColor=colors.HexColor('#526a75')),
 'cell':ParagraphStyle('cell',fontName='VN',fontSize=8.2,leading=11,textColor=INK),
 'th':ParagraphStyle('th',fontName='VNB',fontSize=8.3,leading=11,textColor=colors.white),
 'code':ParagraphStyle('code',fontName='Code',fontSize=7.4,leading=10,spaceBefore=5,spaceAfter=9,backColor=PALE,borderPadding=6),
}
flow=[];md=[];figures=[];tables=[]
def esc(t):return html.escape(str(t))
def p(t):flow.append(Paragraph(esc(t),S['body']));md.append(t+'\n')
def h(t,level=1):flow.append(Paragraph(esc(t),S['h1' if level==1 else 'h2']));md.append('#'*(level+1)+' '+t+'\n')
def code(t,lang='javascript'):
 lines=[]
 for line in t.splitlines():lines.extend(textwrap.wrap(line,94,subsequent_indent='    ',replace_whitespace=False,drop_whitespace=False) or [''])
 flow.append(Preformatted('\n'.join(lines),S['code']));md.append('```'+lang+'\n'+t+'\n```\n')
def table(title,headers,rows,widths=None):
 label=f'Bảng {len(tables)+1} {title}';tables.append(label)
 flow.append(Paragraph(esc(label),S['caption']))
 data=[[Paragraph(esc(v),S['th']) for v in headers]]
 data.extend([[Paragraph(esc(v).replace(', ', ',<br/>') if len(str(v))>140 else esc(v),S['cell']) for v in row] for row in rows])
 t=Table(data,colWidths=widths or [499/len(headers)]*len(headers),repeatRows=1,hAlign='LEFT')
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),ACC),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),('LINEBELOW',(0,0),(-1,0),.5,ACC),('LINEBELOW',(0,1),(-1,-1),.35,colors.HexColor('#d9e4e7')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f6f8f9')])]))
 flow.extend([t,Spacer(1,9)])
 md.append('**'+label+'**\n\n|'+'|'.join(headers)+'|\n|'+'|'.join(['---']*len(headers))+'|\n'+'\n'.join('|'+'|'.join(str(v).replace('|',' / ').replace('\n',' ') for v in row)+'|' for row in rows)+'\n')
def image(name,title,note):
 path=OUT/'images'/name
 with PILImage.open(path) as im:w,hh=im.size
 width=499;height=width*hh/w
 img=Image(str(path),width=width,height=height)
 label=f'Hình {len(figures)+1} {title}';figures.append(label)
 flow.append(KeepTogether([img,Paragraph(esc(label),S['caption'])]));p(note)
 md.append(f'![{label}](images/{name})\n')
def arrow(d,x1,y1,x2,y2,label=''):
 d.add(Line(x1,y1,x2,y2,strokeColor=ACC,strokeWidth=1))
 import math
 a=math.atan2(y2-y1,x2-x1);a1=a+2.65;a2=a-2.65
 d.add(Polygon([x2,y2,x2+6*math.cos(a1),y2+6*math.sin(a1),x2+6*math.cos(a2),y2+6*math.sin(a2)],fillColor=ACC,strokeColor=None))
 if label:d.add(String((x1+x2)/2+3,(y1+y2)/2+7,label,fontName='VN',fontSize=8,fillColor=INK))
def box(d,x,y,w,hh,title,body=()):
 d.add(Rect(x,y,w,hh,rx=4,ry=4,fillColor=PALE,strokeColor=colors.HexColor('#b0c7ce')))
 d.add(String(x+7,y+hh-16,title,fontName='VNB',fontSize=9,fillColor=ACC))
 for i,line in enumerate(body):d.add(String(x+7,y+hh-31-i*12,line,fontName='VN',fontSize=8,fillColor=INK))
def diagram(kind,title):
 if kind=='usecase':
  d=Drawing(499,245);box(d,0,93,100,70,'Khách truy cập',['Không cần tài khoản']);box(d,399,93,100,70,'Quản trị viên',['Phiên và role admin'])
  actions=['Lọc và quay món','Xem quán và công thức','Lưu yêu thích cục bộ','Quản lý danh mục','Duyệt căn cứ nhãn','Ẩn hoặc hiện nội dung']
  for i,a in enumerate(actions):
   y=218-i*35;d.add(Ellipse(249,y,110,13,fillColor=PALE,strokeColor=ACC));d.add(String(249,y-3,a,fontName='VN',fontSize=9,textAnchor='middle'))
   if i<3:arrow(d,100,128,139,y)
   else:arrow(d,399,128,359,y)
 elif kind=='deploy':
  d=Drawing(499,220);box(d,0,130,125,60,'Trình duyệt',['HTML CSS JavaScript']);box(d,179,130,145,60,'Vercel Node Function',['handleRequest và MVC']);box(d,374,130,125,60,'Aiven MySQL',['Danh mục và phiên'])
  arrow(d,125,160,179,160,'HTTPS');arrow(d,324,160,374,160,'TLS')
  box(d,179,15,145,65,'GitHub',['Code schema seed','Không có .env thật']);arrow(d,251,80,251,130,'Build và deploy')
  box(d,0,15,125,65,'Trình duyệt lưu riêng',['Yêu thích và giao diện','Theo origin']);arrow(d,63,130,63,80)
 elif kind=='erd1':
  d=Drawing(499,285)
  for x,y,w,hh,t,b in [(0,195,145,75,'cuisines',['PK id','FK cover_dish_id']), (177,195,145,75,'dishes',['PK id','FK cuisine_id']), (354,195,145,75,'meals',['PK id','label']), (0,20,145,75,'restaurants',['PK id','is_visible revision']), (177,20,145,75,'restaurant_dishes',['PK dish_id restaurant_id','FK tới dishes restaurants']), (354,20,145,75,'dish_meals',['PK dish_id meal_id','FK tới dishes meals'])]:box(d,x,y,w,hh,t,b)
  arrow(d,145,235,177,235,'1 N');arrow(d,249,95,249,195,'N 1');arrow(d,145,57,177,57,'1 N');arrow(d,322,213,380,95,'1 N');arrow(d,426,195,426,95,'1 N')
  d.add(String(0,115,'restaurant_meals nối restaurants với meals theo quan hệ nhiều nhiều',fontName='VN',fontSize=9,fillColor=INK))
 elif kind=='erd2':
  d=Drawing(499,245);box(d,0,155,145,75,'dishes',['PK id']);box(d,177,155,145,75,'recipes',['PK và FK dish_id','base_servings']);box(d,354,155,145,75,'recipe_ingredients',['PK dish_id sort_order','FK dish_id tới recipes'])
  box(d,0,10,145,75,'dish_reviews',['PK dish_id review_key','FK dish_id tới dishes']);box(d,177,10,145,75,'dish_nutrition_profiles',['PK và FK dish_id','profile JSON']);box(d,354,10,145,75,'recipe_steps',['PK dish_id sort_order','FK dish_id tới recipes'])
  arrow(d,145,192,177,192,'1 0..1');arrow(d,322,192,354,192,'1 N');arrow(d,72,155,72,85,'1 N');arrow(d,115,155,220,85,'1 0..1');arrow(d,300,155,400,85,'1 N')
 elif kind=='erd3':
  d=Drawing(499,235);box(d,177,145,145,75,'users',['PK id UNIQUE email','role user hoặc admin'])
  for x,t,b in [(0,'auth_accounts',['FK user_id','Mã băm theo provider']),(177,'auth_sessions',['FK user_id UNIQUE token','expires_at']),(354,'audit danh mục',['FK actor_user_id','before_data after_data'])]:box(d,x,10,145,75,t,b)
  for x in [72,249,426]:arrow(d,249,145,x,85,'1 N')
  d.add(String(0,122,'auth_rate_limits và auth_verifications lưu trạng thái hỗ trợ xác thực',fontName='VN',fontSize=8.7,fillColor=INK))
 else:
  auth=kind=='auth';actors=['Trình duyệt','Route và middleware','Model hoặc Better Auth','MySQL'];d=Drawing(499,275)
  for i,a in enumerate(actors):
   x=12+i*124;d.add(String(x+48,255,a,fontName='VNB',fontSize=8,textAnchor='middle',fillColor=ACC));d.add(Line(x+48,15,x+48,244,strokeColor=colors.HexColor('#c4d1d6')))
  steps=[(0,1,'POST thông tin đăng nhập'),(1,2,'Kiểm tra Origin và định dạng'),(2,3,'Xác minh tài khoản và lưu phiên'),(3,2,'Kết quả xác thực'),(2,1,'Cookie phiên và trạng thái'),(1,0,'200 hoặc lỗi đăng nhập'),(0,1,'GET admin và cookie'),(1,3,'Đọc lại role từ users'),(1,0,'Cho vào hoặc chuyển đăng nhập')] if auth else [(0,1,'POST hoặc PUT và requestId'),(1,2,'Xác thực và validate dữ liệu'),(2,3,'BEGIN và kiểm tra role'),(2,3,'Khóa bản ghi kiểm tra revision'),(2,3,'Ghi quán bữa và audit'),(2,3,'COMMIT hoặc ROLLBACK'),(3,2,'Bản ghi và revision mới'),(2,1,'Kết quả giao dịch'),(1,0,'201 hoặc 200 hoặc 409')]
  for n,(a,b,l) in enumerate(steps):arrow(d,60+a*124,230-n*23,60+b*124,230-n*23,l)
 label=f'Hình {len(figures)+1} {title}';figures.append(label);flow.append(KeepTogether([d,Paragraph(esc(label),S['caption'])]));md.append('**'+label+'**\n\nSơ đồ dựng từ cấu trúc và luồng trong code dự án.\n')
def parse(text):
 para=[];inc=False;cc=[]
 def flush():
  if para:p(' '.join(para));para.clear()
 for line in text.splitlines():
  if line.startswith('```'):
   flush()
   if inc:code('\n'.join(cc));cc=[];inc=False
   else:inc=True
  elif inc:cc.append(line)
  elif not line.strip():flush()
  elif line.startswith('### '):flush();h(line[4:],2)
  elif line.startswith('## '):flush();h(line[3:])
  elif line.startswith('- '):flush();p('• '+line[2:])
  else:para.append(line)
 flush()

class Doc(SimpleDocTemplate):
 def afterFlowable(self,f):
  if isinstance(f,Paragraph) and f.style.name=='h1':
   key='section-'+str(self.seq.nextf('s'));self.canv.bookmarkPage(key);self.canv.addOutlineEntry(f.getPlainText(),key,0,False);self.notify('TOCEntry',(0,f.getPlainText(),self.page,key))
def footer(c,d):
 c.saveState();c.setFont('VN',8);c.setFillColor(colors.HexColor('#71818a'));c.drawString(48,25,'Hôm nay ăn gì · Báo cáo chi tiết · 07/11/2026');c.drawRightString(A4[0]-48,25,str(d.page));c.restoreState()

# Bìa không gán tên trường hay giảng viên chưa được cung cấp.
flow.append(Spacer(1,60));flow.append(Paragraph('BÁO CÁO ĐỒ ÁN',ParagraphStyle('coverlabel',fontName='VNB',fontSize=15,leading=20,textColor=ACC)))
flow.append(Spacer(1,18));flow.append(Paragraph('Xây dựng website<br/>Hôm nay ăn gì',ParagraphStyle('cover',fontName='VNB',fontSize=31,leading=40,textColor=colors.black)))
flow.append(Spacer(1,20));p('Gợi ý món ăn và kết nối thông tin quán cùng công thức nấu ăn')
flow.append(Spacer(1,25));p('Môn học Advanced Web Design · Nhóm 3')
p('Ngày hoàn thiện báo cáo 07/11/2026 · Phiên bản mã nguồn 87a232a')
p('Website https://hom-nay-an-gi-nhom3.vercel.app')
flow.append(Spacer(1,25));table('Thông tin hoàn thiện trước khi nộp',['Nội dung','Thông tin'],[['Trường và khoa','[Điền theo thông tin của nhóm]'],['Giảng viên hướng dẫn','[Điền tên giảng viên]'],['Thành viên và mã sinh viên','[Điền danh sách chính thức]'],['Lớp và học kỳ','[Điền theo yêu cầu môn học]']],[160,339])
flow.append(PageBreak());h('Tóm tắt và phạm vi đánh giá')
p('Đồ án xây dựng website giúp người dùng lựa chọn món ăn theo điều kiện, xem công thức hoặc tìm địa điểm có thông tin món phù hợp. Frontend HTML CSS JavaScript kết hợp backend Node.js theo MVC, MySQL 8.4, Aiven và Vercel. Website không dùng EJS hoặc Express.')
p('Bản báo cáo bổ sung yêu cầu, Use Case, sơ đồ kiến trúc, ERD, từ điển dữ liệu sau migration, phân tích code theo luồng và minh chứng giao diện. Các ảnh khách được chụp từ website production ngày 07/11/2026. Ảnh admin được chụp trên server local cùng mã nguồn và dữ liệu seed trong MySQL cách ly; không coi những ảnh này là bằng chứng ghi dữ liệu production.')
p('Kết quả ngày 06/11/2026 đã ghi nhận 29 test đạt và 1 bỏ qua, cùng kiểm tra thêm sửa quán và đăng xuất thật trên Vercel. Lần chạy lại ngày 07/11/2026 cho 28 đạt, 1 lỗi ở bài mysql-models và 1 bỏ qua. Lỗi mới nằm trong kịch bản cố ý dùng database không tồn tại và phần dọn kết nối; worker chờ lâu được dừng riêng. Chưa kết luận website production có cùng lỗi trong luồng bình thường. Chi tiết và log nằm ở chương kiểm thử.')
p('Giới hạn phạm vi: yêu thích vẫn lưu trên trình duyệt; không có tài khoản khách đồng bộ, đơn hàng, thanh toán hoặc điều phối shipper. Nút GrabFood và ShopeeFood mở nền tảng ngoài. Thông tin nguồn và dinh dưỡng cần được giữ đúng phiên bản áp dụng.')
flow.append(PageBreak());flow.append(Paragraph('Mục lục',S['h1']));toc=TableOfContents();toc.levelStyles=[ParagraphStyle('toc',fontName='VN',fontSize=10,leading=16,leftIndent=0,firstLineIndent=0,spaceBefore=5)];flow.append(toc);flow.append(PageBreak())

base=(ROOT/'output/bao-cao-2026-11-07/Bao_cao_Hom_nay_an_gi.md').read_text(encoding='utf-8')
sections=re.split(r'(?m)^## ',base)
schema=json.loads((OUT/'schema-current.json').read_text());columns=defaultdict(list)
for row in schema['columns']:columns[row['TABLE_NAME']].append(row)
roles={
 'schema_versions':'Ghi migration đã áp dụng để tránh sửa cấu trúc lặp.', 'seed_imports':'Lưu dấu nguồn seed, hash và số lượng nhập.', 'dataset_documents':'Lưu tài liệu thứ tự và metadata có cấu trúc JSON.',
 'meals':'Danh mục bữa ăn và nhãn hiển thị.', 'cuisines':'Danh mục nền ẩm thực và món ảnh bìa.', 'dishes':'Danh mục món, nguồn ảnh, trạng thái và revision.', 'dish_meals':'Nối món với nhiều bữa ăn theo thứ tự.',
 'restaurants':'Danh mục địa điểm và thông tin biên tập.', 'restaurant_meals':'Nối quán với bữa gợi ý.', 'restaurant_dishes':'Đối chiếu món hoặc biến thể bán tại quán.',
 'recipes':'Công thức gốc theo món và khẩu phần.', 'recipe_ingredients':'Nguyên liệu có số lượng số hoặc văn bản.', 'recipe_steps':'Các bước chế biến theo thứ tự.', 'dish_reviews':'Căn cứ và trạng thái nhãn theo món.', 'dish_nutrition_profiles':'Hồ sơ dinh dưỡng theo phiên bản tham khảo.',
 'users':'Hồ sơ tài khoản và vai trò.', 'auth_accounts':'Thông tin xác thực của provider, gồm mã băm mật khẩu.', 'auth_sessions':'Phiên đăng nhập với thời hạn và token duy nhất.', 'auth_verifications':'Bản ghi xác minh phục vụ thư viện auth.', 'auth_rate_limits':'Bộ đếm tần suất lưu tại database.',
 'favorite_dishes':'Dự phòng yêu thích món theo tài khoản; chưa nối vào chức năng khách.', 'favorite_restaurants':'Dự phòng yêu thích quán theo tài khoản; chưa nối vào chức năng khách.',
 'restaurant_audit':'Lịch sử thêm sửa quán và người thực hiện.', 'dish_audit':'Lịch sử thêm sửa món và người thực hiện.', 'admin_catalog_versions':'Phiên bản và nhận diện request ghi danh mục.', 'admin_catalog_audit':'Lịch sử liên kết công thức và căn cứ nhãn.'}
meaning={'id':'Định danh bản ghi','dish_id':'Mã món liên quan','restaurant_id':'Mã quán liên quan','meal_id':'Mã bữa ăn','cuisine_id':'Mã nền ẩm thực','user_id':'Tài khoản sở hữu','actor_user_id':'Người thực hiện thay đổi','name':'Tên hiển thị','description':'Mô tả nội dung','source_record':'Bản ghi nguồn ban đầu','provenance':'Nguồn gốc dữ liệu','revision':'Phiên bản chống ghi đè','updated_at':'Thời điểm cập nhật','created_at':'Thời điểm tạo','is_visible':'Trạng thái công khai','admin_details':'Trường bổ sung biên tập dạng JSON','sort_order':'Thứ tự hiển thị','email':'Email duy nhất của tài khoản','role':'Vai trò user hoặc admin','password_hash':'Cột cũ để tương thích; auth mới dùng auth_accounts.password','password':'Mã băm mật khẩu do Better Auth quản lý','token':'Mã phiên nhạy cảm không đưa vào log/báo cáo','before_data':'Dữ liệu trước thay đổi','after_data':'Dữ liệu sau thay đổi','match_type':'Bán đúng món hoặc biến thể liên quan','price_vnd':'Giá riêng mỗi phần nếu có căn cứ','price_label':'Khoảng giá tham khảo của quán','price_tier':'Nhóm khoảng giá để lọc','base_servings':'Khẩu phần gốc từ 1 đến 12','amount_min':'Lượng số hoặc đầu dưới của khoảng','amount_max':'Đầu trên của khoảng nếu có','amount_text':'Định lượng văn bản không nhân tỷ lệ','unit':'Đơn vị nguyên liệu','title':'Tiêu đề bước','instruction':'Nội dung bước nấu','evidence':'Căn cứ và phạm vi nguồn','profile':'Số liệu dinh dưỡng có phạm vi','review_key':'Loại nhãn ăn uống','status':'Trạng thái xác minh căn cứ','expires_at':'Thời điểm hết hạn','kind':'Nhóm danh mục quản trị','entity_key':'Mã mục trong nhóm','last_request_id':'UUID yêu cầu ghi gần nhất','last_actor_id':'Người gửi yêu cầu gần nhất','last_payload':'Nội dung yêu cầu gần nhất để chống ghi lặp','count':'Số lượt trong cửa sổ','last_request':'Mốc lần yêu cầu gần nhất','key':'Khóa bộ đếm tần suất','email_verified':'Trạng thái email đã xác minh','cover_dish_id':'Mã món dùng làm ảnh bìa','offering':'Tên phiên bản món trong thực đơn','source_url':'URL nguồn công thức','source_label':'Tên nguồn công thức','prep_time':'Thời gian chuẩn bị dạng văn bản','cook_time':'Thời gian nấu dạng văn bản','soak_note':'Thời gian ngâm hoặc ủ riêng','tip':'Mẹo chế biến','address':'Địa chỉ hoặc chi nhánh','area':'Khu vực tỉnh thành','category':'Nhóm món của quán','original_category':'Nhóm món giữ từ nguồn','verification':'Tình trạng dữ liệu nguồn','photo':'Thông tin ảnh và loại minh họa','website':'URL website chính thức nếu có','label':'Nhãn hiển thị','document':'Nội dung metadata JSON','version':'Mã migration','applied_at':'Mốc áp dụng migration','seed_key':'Mã nguồn seed','content_hash':'SHA256 của nguồn seed','counts':'Số lượng nhập theo loại','imported_at':'Thời điểm nhập seed'}
usecases=[
 ('UC01 Quay món','Khách','Có danh mục tải thành công','Chọn điều kiện → xem số món → quay → xem kết quả','Không có món thì khóa quay; không tự bỏ lọc'),
 ('UC02 Xem quán theo món','Khách','Món đang công khai','Mở kết quả → tải API liên kết → mở chi tiết quán','Không có liên kết phải báo rõ; không suy đoán quán bán'),
 ('UC03 Đọc công thức','Khách','Món và công thức được công bố','Mở công thức → đổi người ăn → đánh dấu bước','Chưa có công thức thì hiện trạng thái cập nhật'),
 ('UC04 Lưu yêu thích','Khách','Trình duyệt cho phép storage','Bấm trái tim → ghi ID → cập nhật trạng thái','Ghi thất bại phải báo lỗi, không hiện lưu giả'),
 ('UC05 Đăng nhập','Admin','Tài khoản được cấp role admin','Nhập email mật khẩu → xác thực → cookie → kiểm tra role','Sai mật khẩu 401; thiếu quyền 403; quá lượt 429'),
 ('UC06 Thêm sửa quán','Admin','Phiên hợp lệ và quyền admin','Mở form → validate → transaction → lưu audit → tải lại','Dữ liệu sai 400; revision cũ 409; lỗi thì rollback'),
 ('UC07 Duyệt nhãn','Admin','Có nguồn và định lượng đủ căn cứ','Chọn món → nhập nguồn phạm vi → kiểm tra → công bố','Không đủ căn cứ thì không gán; thu hồi khi cần'),
 ('UC08 Đăng xuất','Admin','Có phiên đăng nhập','Bấm đăng xuất → server thu hồi phiên → về đăng nhập','Nếu lỗi không giả vờ đã thu hồi thành công')]

for chunk in sections[1:]:
 title=chunk.splitlines()[0]
 if title=='Thông tin báo cáo':continue
 if title.startswith('Phụ lục'):h('Phụ lục A Code tiêu biểu');parse('\n'.join(chunk.splitlines()[1:]));continue
 parse('## '+chunk)
 if title.startswith('1 '):
  h('1.4 Yêu cầu chức năng và tiêu chí chấp nhận',2)
  table('Yêu cầu chức năng',['Mã','Yêu cầu và kết quả chấp nhận','Cách đối chiếu'],[
   ['FR01','Danh mục đọc từ MySQL, không dùng bản JSON cũ khi API lỗi','Model và HTTP 503'],['FR02','Quay trong đúng tập đã lọc, không bỏ điều kiện ngầm','spin-filters và test tập món'],['FR03','Hiện quán có liên kết đúng món, tách biến thể liên quan','restaurant_dishes.match_type'],['FR04','Công thức có nguồn và tính lượng cho 1 đến 12 người','recipe.js và test định lượng'],['FR05','Nhãn có popup và phạm vi áp dụng rõ','dish_reviews và validators'],['FR06','Yêu thích lưu ID cục bộ, có phản hồi lỗi ghi','favorites.js'],['FR07','Đăng nhập tạo phiên thật và kiểm tra role ở server','Better Auth và middleware'],['FR08','Ghi danh mục có transaction, revision và audit','Models quản trị và test rollback'],['FR09','Ẩn hiện tác động đồng bộ lên nội dung công khai','is_visible và test visibility'],['FR10','Đăng xuất thu hồi phiên ở MySQL','Kiểm tra phiên và mở lại admin']],[44,289,166])
  h('1.5 Yêu cầu phi chức năng và phạm vi chứng minh',2)
  table('Yêu cầu chất lượng',['Thuộc tính','Yêu cầu','Giới hạn bằng chứng'],[['An toàn','Phân quyền server, tham số SQL, TLS và cookie phù hợp','Chưa có audit bảo mật độc lập'],['Toàn vẹn','Ghi nguyên tử và ngăn ghi đè phiên bản cũ','Test transaction và 409'],['Khả dụng','Thông báo lỗi thay vì dùng dữ liệu cũ giả thành công','Chưa chứng minh uptime dài hạn'],['Hiệu năng','Giới hạn kết nối và có dọn idle','Chưa có kiểm thử tải lớn hoặc SLA'],['Sử dụng','Responsive, nhãn điều khiển và giảm chuyển động','Không khẳng định chứng nhận accessibility'],['Bảo trì','MVC, migration, seed, test và tài liệu riêng','Thành viên vẫn phải tự dựng môi trường']],[76,231,192])
  diagram('usecase','Use Case tổng quan theo hai vai trò')
  table('Đặc tả Use Case chính',['Use Case','Tác nhân và tiền điều kiện','Luồng chính','Ngoại lệ'],[[a,b+'; '+c,d,e] for a,b,c,d,e in usecases],[95,119,152,133])
  p('Quy tắc nghiệp vụ xuyên suốt: không bịa dữ liệu quán; giá quán và giá từng món là hai loại thông tin; một nhãn của phiên bản nguồn không tự áp dụng cho mọi công thức hoặc mọi quán. Ẩn nội dung là thay đổi quyền công khai, không phải xóa dữ liệu. Khách không được quyết định role bằng dữ liệu gửi từ trình duyệt.')
 if title.startswith('2 '):
  diagram('deploy','Kiến trúc triển khai và ranh giới lưu trữ')
  table('Lý do lựa chọn kỹ thuật',['Quyết định','Lợi ích trong đồ án','Đánh đổi'],[['HTML và JavaScript thuần','Giữ giao diện đã xây, không cần chuyển template','Cần tự quản lý trạng thái và trạng thái lỗi'],['node:http thay Express','Ít lớp trung gian, dùng lại handler trên Vercel','Tự xử lý body, route và MIME'],['MySQL thay dữ liệu JSON runtime','Quan hệ, foreign key, transaction và phiên thật','Phải quản lý schema và kết nối'],['Better Auth','Tái sử dụng cơ chế phiên và xác thực của thư viện','Cần cấu hình bảng và Origin chính xác'],['Aiven và Vercel','Tách database online khỏi máy thành viên','Có giới hạn tài nguyên và độ trễ mạng']],[118,196,185])
  p('View chỉ điều khiển trải nghiệm và gửi dữ liệu; không được quyết định quyền ghi. Route chọn controller, controller gọi validator và Model, còn Model chịu trách nhiệm tính nguyên tử. Tên thư mục giúp phân trách nhiệm nhưng tính đúng đắn vẫn phụ thuộc việc kiểm tra tại server. Các trường hợp nghiệp vụ phức tạp như thu hồi căn cứ sau sửa công thức nằm ở luồng Model quản trị, không chỉ xử lý bằng cách ẩn nút.')
 if title.startswith('3 '):
  h('3.6 Minh họa giao diện và nhiệm vụ từng màn hình',2)
  image('01-trang-chu.jpg','Trang chủ trên website production','Ảnh chụp ngày 07/11/2026. Điểm vào chính là Bất ngờ đi; Tùy chọn được thu gọn để không làm chậm người muốn chọn nhanh. Lời chào phụ thuộc giờ thiết bị, không phải một giá trị cố định trong database.')
  image('02-danh-muc-mon.jpg','Danh mục món và các bộ lọc','Danh mục được dựng từ dữ liệu động. Khi demo cần thử kết hợp Có công thức với Món chay, rồi xóa bộ lọc; số lượng và tập món phải thay đổi cùng nhau. Chữ quốc gia và icon bữa ăn cần giữ ý nghĩa ngay cả khi không phân biệt màu.')
  image('03-cong-thuc.jpg','Thông tin công thức xôi xoài','Ảnh phần đầu trang cho thấy nhãn, nguồn ngữ cảnh món và khẩu phần. Phần nguyên liệu và bước nằm tiếp bên dưới. Hình minh họa món không phải bằng chứng về suất ăn của một nhà hàng.')
  image('04-quan-an.jpg','Danh sách quán có tìm kiếm và phân trang','Thông tin được đọc từ API. Bữa và giá tham khảo hỗ trợ thu hẹp kết quả; chưa có dữ liệu không được tự chuyển thành giá cố định. Danh sách không tự khẳng định quán đang mở cửa thời gian thực.')
  image('05-admin-login-local.jpg','Trang đăng nhập trên môi trường thử cách ly','Ảnh local dùng cùng giao diện với production và chưa nhập thông tin xác thực. Tài khoản thử được tạo riêng, database và khóa phiên tạm đã được dọn sau phiên chụp. Ảnh này minh họa giao diện, không thay thế kiểm thử đăng nhập production ngày 06/11.')
  image('06-admin-overview-local.jpg','Tổng quan quản trị với dữ liệu seed','Các số 105 món, 105 quán, 14 công thức và 109 liên kết là số lượng danh mục, không phải lượt xem hoặc đơn hàng. Ảnh được chụp local sau đăng nhập bằng tài khoản thử, không chứa tài khoản thật hoặc token.')
  image('07-admin-restaurants-local.jpg','Danh sách quản trị quán','Admin có phân trang, tìm kiếm và lọc hiển thị. Dữ liệu ở ảnh là seed cách ly. Các thao tác ghi production đã được kiểm tra riêng và được mô tả trong chương kiểm thử.')
  image('08-admin-form-local.jpg','Form thêm quán và trạng thái hiển thị','Mở form để minh họa, không bấm lưu và không tạo quán mới trong quá trình chụp. Các trường bắt buộc được đánh dấu; trường chưa biết để trống. Trạng thái ẩn giữ dữ liệu trong admin và loại khỏi các luồng công khai.')
  h('3.7 Tiêu chí kiểm tra bố cục điện thoại',2)
  p('Ở màn hình nhỏ cần kiểm tra menu có mở được bằng bàn phím/cảm ứng, nút quay không bị che, dropdown không tràn ngang, modal có vùng cuộn và nút đóng luôn tiếp cận được. Công thức cần xếp ảnh và thông tin theo chiều dọc; bảng admin cần cách cuộn hoặc trình bày không làm mất thao tác sửa. Báo cáo không đưa ảnh thử kích thước 390 pixel vào làm bằng chứng vì ảnh thu được không đủ chất lượng để kết luận đúng về viewport điện thoại.')
 if title.startswith('4 '):
  h('4.4 Ví dụ chạy qua bộ lọc và thứ tự ưu tiên',2)
  p('Giả sử tập món gốc có A, B và C. A có công thức và nhãn chay; B có công thức nhưng không có căn cứ chay; C chay nhưng chưa có công thức. Chọn Món chay và Có công thức chỉ còn A. Nếu A là món vừa quay trước đó, tầng ưu tiên cuối vẫn cho phép A vì không có món thay thế trong tập hợp lệ. Không được lấy B chỉ để tránh lặp. Ví dụ này là minh họa thuật toán, không phải ba bản ghi mới trong database.')
  code("options = SpinFilters.parse(new URLSearchParams(location.search));\nvalidDishes = SpinFilters.apply(FOOD.DISHES, options);\n// Trước khi gọi pickDish cần xử lý tập rỗng.\nif (validDishes.length === 0) showEmptyState();\nelse selectedDish = App.pickDish(validDishes);",'javascript minh họa luồng')
  p('Đoạn trên minh họa sự nối kết giữa các hàm, không được ghi là trích nguyên file. Code thật của parse, apply và pickDish nằm ở phụ lục. Độ phức tạp của lọc và tạo các tầng chọn là O(n) theo số món. Với 105 món, cách làm đơn giản dễ kiểm tra hơn việc thêm hệ thống đề xuất phức tạp chưa có dữ liệu hành vi.')
 if title.startswith('7 '):
  h('7.5 ERD theo nhóm dữ liệu',2)
  diagram('erd1','Quan hệ danh mục món quán và bữa ăn')
  p('Ký hiệu 1 N chỉ một-nhiều; bảng nối tạo quan hệ nhiều-nhiều giữa hai bảng chính. Mũi tên trong hình thể hiện hướng tham chiếu hoặc liên kết logic. cuisines.cover_dish_id còn tham chiếu ngược tới dishes làm món bìa; foreign key này được thêm sau khi tạo dishes để xử lý vòng tham chiếu. Danh sách khóa ngoại đầy đủ được trích từ schema đã áp dụng ở phụ lục dữ liệu.')
  diagram('erd2','Quan hệ công thức nguyên liệu bước và căn cứ')
  p('Mỗi dish_id có tối đa một recipe đang được quản lý. recipe_ingredients và recipe_steps dùng khóa ghép với sort_order để giữ thứ tự. dish_reviews có thể có nhiều review_key cho cùng một món. Giá trị 0..1 diễn đạt một món có thể chưa có công thức hoặc hồ sơ dinh dưỡng.')
  diagram('erd3','Quan hệ tài khoản phiên và lịch sử quản trị')
  h('7.6 Từ điển dữ liệu sau đầy đủ migration',2)
  p('Bảng dưới lấy từ information_schema của MySQL cách ly sau applySchema; không lấy cấu trúc cũ trong schema.sql rồi bỏ qua migration. PRI là thành phần khóa chính, UNI là khóa duy nhất, MUL là cột thuộc chỉ mục không duy nhất. Cột FK có tham chiếu được nêu kèm. Ký hiệu NULL là được phép thiếu; NOT NULL là bắt buộc. Mặc định không được diễn giải là giá trị thực tế của một bản ghi.')
  for name in sorted(columns):
   h(name,2);p(roles.get(name,'Bảng thành phần của hệ thống.'))
   rows=[]
   for c in columns[name]:
    fks=[f['REFERENCED_TABLE_NAME']+'.'+f['REFERENCED_COLUMN_NAME'] for f in schema['foreignKeys'] if f['TABLE_NAME']==name and f['COLUMN_NAME']==c['COLUMN_NAME']]
    key=c['COLUMN_KEY'] or '—'
    if fks:key+='; FK '+', '.join(fks)
    note=meaning.get(c['COLUMN_NAME'],'Thông tin '+c['COLUMN_NAME'].replace('_',' ')+' theo schema.')
    if c['COLUMN_DEFAULT'] is not None:note+=' Mặc định '+str(c['COLUMN_DEFAULT'])+'.'
    if c['EXTRA']:note+=' '+c['EXTRA']+'.'
    rows.append([c['COLUMN_NAME'],c['COLUMN_TYPE'],('NULL' if c['IS_NULLABLE']=='YES' else 'NOT NULL')+'; '+key,note])
   table('Cấu trúc '+name,['Trường','Kiểu MySQL','Ràng buộc','Ý nghĩa'],rows,[103,103,111,182])
  h('7.7 Ràng buộc và chuẩn hóa cần lưu ý',2)
  p('Bảng nối tránh việc lưu một chuỗi tên món hoặc tên bữa không kiểm tra được. Foreign key bảo vệ mã tham chiếu; index hỗ trợ tìm và nối theo cột thường dùng. Không có ON DELETE CASCADE trên mọi quan hệ: không được giả định xóa một quán sẽ tự dọn toàn bộ lịch sử. Cách vận hành thường dùng là ẩn hoặc ngừng công bố. Giá món có CHECK không âm; khẩu phần gốc có CHECK từ 1 đến 12; nguyên liệu bắt buộc đúng một nhánh văn bản hoặc định lượng số hợp lệ.')
  p('Một số giá trị có cấu trúc thay đổi vẫn dùng JSON, như nguồn, căn cứ hoặc thông tin biên tập. Cách này thuận lợi khi giữ phạm vi và lịch sử nguồn nhưng không thay thế cột quan hệ dùng để nối. Sau migration xác thực, users.password_hash được phép NULL; mã băm dùng bởi Better Auth nằm trong auth_accounts.password. Không mô tả cột này như mật khẩu dạng rõ.')
 if title.startswith('8 '):
  diagram('auth','Trình tự đăng nhập và kiểm tra role')
  table('Xử lý trạng thái xác thực',['Trường hợp','Kết quả','Điểm kiểm soát'],[['Sai email hoặc mật khẩu','401 với thông báo chung','Không trả hash hoặc phân biệt email có tồn tại'],['Không có phiên khi gọi API admin','401','requireAdmin phía server'],['Role không phải admin','403','Đọc users mỗi request'],['Origin không khớp domain chính','403','authOrigin và header Origin'],['Gửi sai Content Type','415','JSON trước khi chuyển Better Auth'],['Thử quá giới hạn','429 và thông tin thử lại nếu có','Rate limit lưu MySQL'],['Đăng xuất thành công','Phiên bị thu hồi và trang admin bị chặn','MySQL auth_sessions và cookie']],[153,161,185])
  p('Ví dụ đổi tên miền: frontend gửi Origin của tên mới trong khi BETTER_AUTH_URL vẫn là tên cũ sẽ bị server từ chối. Vì vậy đổi DNS/alias chưa đủ; phải cập nhật origin và triển khai lại. Không giải quyết bằng cách chấp nhận mọi Origin hoặc tắt Secure cookie. Cách giữ nguyên giao diện không có nghĩa giữ nguyên cấu hình môi trường khi địa chỉ website thay đổi.')
 if title.startswith('9 '):
  diagram('write','Trình tự thêm sửa quán có transaction')
  h('9.5 Ví dụ hợp đồng ghi và xung đột',2)
  code('{\n  "name": "Tên quán đã đối chiếu",\n  "address": "Địa chỉ có căn cứ",\n  "area": "Đà Nẵng",\n  "category": "Món chính",\n  "meals": ["sang", "trua"],\n  "isVisible": false,\n  "requestId": "UUID v4 của lần ghi"\n}', 'json minh họa các trường chính')
  p('Payload trên là phần minh họa, không phải toàn bộ trường form và không phải dữ liệu quán thật. Khi sửa cần revision hiện có. Ví dụ hai admin cùng mở revision=3: người thứ nhất lưu làm revision=4, người thứ hai vẫn gửi 3 thì bị 409. Trình duyệt cần tải dữ liệu mới và cho người dùng đối chiếu; không tự gửi lại bằng revision mới để che mất xung đột.')
  p('Trong transaction, việc sửa trường chính, thay các bữa liên quan và ghi audit phải thành một đơn vị. Nếu INSERT bữa bị foreign key từ chối, mọi UPDATE trước đó phải rollback. Không gọi mỗi câu qua một connection tùy ý vì như vậy không bảo đảm cùng transaction. finally release là bắt buộc để tránh giữ connection đã hoàn tất.')
 if title.startswith('10 '):
  table('Từ giao diện đến lớp xử lý',['Nhiệm vụ','Frontend','Route hoặc controller','Model'],[['Quay món','home.js result.js spin-filters.js','GET dữ liệu động và API món','food.model.js dish.model.js'],['Quán liên quan','result.js restaurant.js','dish.controller.js','restaurant.model.js'],['Khẩu phần','recipe.js','GET /js/recipes.js','recipe.model.js'],['Thêm sửa quán','admin.js','admin-restaurant.controller.js','admin-restaurant.model.js'],['Công thức và căn cứ','admin.js và module hỗ trợ','admin-catalog.controller.js','admin-catalog.model.js'],['Quyền admin','admin-session.js','middleware/auth.js','Better Auth và users']],[94,123,152,130])
  p('Ví dụ luồng sửa quán: sự kiện submit đọc giá trị form → frontend tạo JSON và giữ requestId → fetch PUT → route admin bắt buộc phiên → controller gọi validateRestaurant → Model khóa bản ghi và so revision → transaction commit → controller trả record → frontend thay dữ liệu và render lại. Không có bước nào cần reload seed JSON trên đĩa để cập nhật quán vừa lưu.')
 if title.startswith('11 '):
  table('Biến môi trường và phạm vi lưu',['Tên','Mục đích','Quy tắc chia sẻ'],[['DB_HOST DB_PORT DB_NAME','Địa chỉ và database MySQL','Không hardcode trong frontend'],['DB_USER DB_PASSWORD','Tài khoản backend truy cập MySQL','Không đưa mật khẩu lên Git hoặc báo cáo'],['DB_SSL_CA','Chứng chỉ CA kiểm tra TLS','Dùng đúng cấu hình server, không tắt xác minh'],['BETTER_AUTH_SECRET','Khóa xác thực phiên','Giữ riêng ở môi trường chạy'],['BETTER_AUTH_URL','Origin website chính','HTTPS production; cập nhật khi đổi domain'],['NODEJS_HELPERS','Giữ raw body cho handler HTTP','Theo hướng dẫn cấu hình triển khai'],['HOST PORT','Địa chỉ server local','Không sao chép làm cổng Function Vercel']],[139,172,188])
  p('Quy trình phát hành khuyến nghị: kiểm tra working tree → chạy test và build → sao lưu database nếu có migration → push đúng branch → đặt biến môi trường trên project → deploy → theo dõi đến Ready → thử API công khai và quyền admin → thử ghi riêng khi được phép → dọn dữ liệu thử. Không coi trạng thái build Ready là bằng chứng rằng database đã kết nối hoặc nghiệp vụ đã đúng.')
 if title.startswith('12 '):
  table('Phân biệt các nguyên nhân giao diện chưa có dữ liệu',['Dấu hiệu','Khả năng cần kiểm tra','Bằng chứng cần lấy'],[['HTML 200, API 503','Kết nối MySQL hoặc truy vấn lỗi','Log mã lỗi server; không xuất mật khẩu'],['Auth 403 sau đổi domain','Origin không khớp','BETTER_AUTH_URL và Origin request'],['API 200 nhưng trang trống','Lỗi JavaScript hoặc DOM','Console và response shape'],['Ảnh hỏng, chữ vẫn có','URL ảnh hoặc tài nguyên ngoài','Network ảnh và placeholder'],['Trang admin chậm nhưng rồi vào','Độ trễ xác thực, request dữ liệu hoặc khởi động','Timing từng request, chưa đo thì chưa kết luận']],[142,176,181])
 if title.startswith('13 '):
  h('13.4 Chạy lại ngày 07 tháng 11 và vấn đề còn mở',2)
  p('Nguồn bằng chứng mới là test-2026-11-07.log. npm test kết thúc mã lỗi 1, ghi 30 test, 28 pass, 1 fail và 1 skip. Bài fail là MySQL models preserve API contracts use live normalized values and never fall back to JSON. Kịch bản cố ý chuyển DB_NAME sang hnag_database_does_not_exist; stack trace ghi ER_BAD_DB_ERROR tại closeDatabase và finally của tests/mysql-models.test.js. Worker bị chờ lâu và đã được dừng riêng để runner hoàn tất, không dừng dịch vụ MySQL thật.')
  p('Không được dùng kết quả 29 pass ngày 06/11 thay cho lần chạy mới này. Cũng chưa đủ căn cứ kết luận mọi thao tác website production bị lỗi: các bài ghi quán, auth, rollback, Vercel adapter và visibility vẫn pass; API production mới kiểm tra trả đúng trạng thái. Cần tái hiện riêng đường lỗi cấu hình database và việc đóng pool, đặt timeout hữu hạn cho bài test, kiểm tra các promise còn chờ và xác nhận không kẹt queue khi kết nối ban đầu thất bại. Báo cáo này không sửa code hoặc redeploy để che kết quả test.')
  live=json.loads((OUT/'live-check-2026-11-07.json').read_text())
  table('Kiểm tra HTTP production ngày 07 tháng 11',['Đường dẫn','Mong đợi','Quan sát','Độ trễ một mẫu'],[[x['path'],{'/':'200','/api/dishes':'200 và 105 món','/api/restaurants':'200 và 105 quán','/admin.html':'302 về đăng nhập','/api/admin/me':'401','/.env':'404'}[x['path']],str(x['status'])+(f"; {x['count']} mục" if 'count'in x else '')+(('; '+x['location'])if x.get('location')else ''),str(x['ms'])+' ms']for x in live['results']],[143,137,137,82])
  p('Các thời gian trên là một mẫu đo tuần tự từ máy kiểm tra, không phải p95, SLA hay kết quả load test. Chỉ dùng chúng để chứng minh request đã trả về tại thời điểm đo.')
  table('Kịch bản kiểm thử và kết quả có nguồn',['Mã','Tiền điều kiện hoặc thao tác','Kết quả mong đợi','Quan sát và nguồn'],[
   ['TC01','Quay với điều kiện chay và có công thức','Mọi kết quả thuộc tập hợp lệ','Pass trong tests/spin-filters.test.js'],['TC02','Danh mục tìm và phân trang','Không mất hoặc lặp bản ghi','Pass nhóm restaurant tests 07/11'],['TC03','Đổi khẩu phần gốc sang số người mới','Số lượng đổi tỷ lệ, văn bản giữ nguyên','Code và test recipe/seed; chưa có benchmark thao tác UI toàn bộ công thức'],['TC04','Gọi API admin chưa đăng nhập','401','HTTP production 07/11 quan sát 401'],['TC05','Ghi không đủ quyền hoặc sai Origin','403','Pass auth và admin write tests 07/11'],['TC06','Thêm quán thử ẩn trên Vercel','201 và revision 1, không công khai','Đã đối chiếu Aiven 06/11'],['TC07','Sửa quán thử đổi tên và bữa','Revision 2, audit create/update','Đã đối chiếu Aiven và tải lại trang 06/11'],['TC08','Đăng xuất rồi mở lại admin','Phiên bị thu hồi, về đăng nhập','Đã kiểm tra production 06/11'],['TC09','Hai người gửi cùng revision','Một thành công, một 409','Pass nhóm admin restaurant tests 07/11'],['TC10','Lỗi bước ghi liên quan trong transaction','Không lưu dở bản chính hoặc audit','Pass test rollback 07/11'],['TC11','Ẩn món hoặc quán','Loại khỏi dữ liệu công khai liên quan','Pass visibility test 07/11'],['TC12','Database không tồn tại rồi dọn pool','503 có kiểm soát và test kết thúc','Chưa đạt; ER_BAD_DB_ERROR và worker chờ trong lần chạy 07/11'],['TC13','Storage bị chặn khi lưu yêu thích','Báo lỗi không giả thành công','Có nhánh xử lý code; chưa ghi nhận kiểm thử tay mới 07/11'],['TC14','Khả năng chịu tải nhiều người dùng','Không có ngưỡng nghiệm thu đã chốt','Chưa thực hiện load test; không ghi Pass']],[43,149,137,170])
 if title.startswith('14 '):
  table('Ưu tiên xử lý sau bản báo cáo',['Mức','Hạng mục','Điều kiện hoàn tất'],[['Cao','Đường lỗi và dọn pool trong test mysql-models','Chạy riêng có timeout, sửa đúng nguyên nhân, full suite kết thúc'],['Cao','Thông báo lỗi tải danh mục thay vì trang trống','API lỗi có trạng thái rõ và nút thử lại'],['Vừa','Đo chậm đăng nhập theo từng request','Có thời gian auth, me và tải danh mục'],['Vừa','Rà soát dữ liệu kinh doanh','Nguồn và ngày đối chiếu cho giá, địa chỉ, món bán'],['Sau','Tài khoản khách đồng bộ yêu thích','Có yêu cầu và API quyền sở hữu rõ'],['Sau','Đơn hàng và đối tác giao đồ ăn','Có API được phép cùng dữ liệu thực']],[45,231,223])
 if title.startswith('15 '):
  p('Để thuyết trình code trong 10 phút: bắt đầu từ sơ đồ MVC; mở server/app.js chỉ ra route và dữ liệu động; mở SpinFilters.apply và App.pickDish giải thích tập hợp lệ; mở recipe.js giải thích tỷ lệ; mở requireAdmin chứng minh quyền ở server; mở writeRestaurant giải thích transaction, revision và audit; kết thúc bằng ảnh Vercel và bảng test gồm cả lỗi còn mở. Tránh đọc lần lượt mọi dòng code mà không gắn với thao tác người dùng.')
 if title.startswith('16 '):
  p('Kết luận cập nhật ngày 07/11: các chức năng chính đã có và các luồng production đã được kiểm tra theo mốc ghi nhận. Tuy nhiên lần chạy test mới chưa xanh hoàn toàn; cần xử lý bài mysql-models trước khi khẳng định bộ kiểm thử hiện tại đạt tất cả. Đây là một giới hạn xác minh cụ thể, không nên bỏ qua trong nghiệm thu kỹ thuật.')

h('Phụ lục B Khóa ngoại đầy đủ')
table('Khóa ngoại sau migration',['Bảng','Cột','Tham chiếu'],[[x['TABLE_NAME'],x['COLUMN_NAME'],x['REFERENCED_TABLE_NAME']+'.'+x['REFERENCED_COLUMN_NAME']]for x in schema['foreignKeys']],[163,155,181])
h('Phụ lục C Tài liệu minh chứng và cách tái lập')
p('schema-current.json là metadata cấu trúc trích từ MySQL thử sau migration, không chứa bản ghi hoặc token. live-check-2026-11-07.json ghi URL tương đối, mã HTTP và thời gian mẫu. test-2026-11-07.log là đầu ra lần test mới có một lỗi, không được đổi tên thành log đạt. Các ảnh 01 đến 04 là production; ảnh 05 đến 08 là local cách ly. Mã nguồn đầy đủ vẫn ở gói ZIP phiên bản 87a232a được cung cấp cùng bản báo cáo trước.')
p('Tái lập môi trường: npm ci; tạo cấu hình riêng từ .env.example; dùng database phát triển của mình theo database/README.md; db:check trước khi nhập; npm test dùng instance tạm. Không dùng snapshot schema làm bản backup dữ liệu Aiven và không đưa file .env.capture-session hoặc khóa tạo cho ảnh admin vào bộ minh chứng. Môi trường ảnh local đã được dừng và dọn sau chụp.')
h('Danh mục hình và bảng')
for label in figures:p(label)
for label in tables:p(label)

pdf=OUT/'Bao_cao_chi_tiet_Hom_nay_an_gi.pdf'
doc=Doc(str(pdf),pagesize=A4,leftMargin=48,rightMargin=48,topMargin=43,bottomMargin=45,title='Báo cáo đồ án Hôm nay ăn gì',author='Nhóm 3')
doc.multiBuild(flow,onFirstPage=footer,onLaterPages=footer)
(OUT/'Bao_cao_chi_tiet_Hom_nay_an_gi.md').write_text('# Báo cáo đồ án Hôm nay ăn gì\n\n'+'\n'.join(md),encoding='utf-8')
print(json.dumps({'pdf':str(pdf),'figures':len(figures),'tables':len(tables),'schemaTables':len(columns)},ensure_ascii=False))
