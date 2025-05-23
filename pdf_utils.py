from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm

def create_weekend_pdf(data, output_path):
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    x, y = 20 * mm, height - 20 * mm

    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width / 2, y, "주말·체험영농계획서")
    y -= 20

    c.setFont("Helvetica", 11)
    def draw(label, val): nonlocal y; c.drawString(x, y, f"{label}: {val}"); y -= 12

    draw("① 취득 대상 농지", f"{data.get('region')} {data.get('town')} {data.get('village')} {data.get('lot')}, {data.get('area')}㎡, 지분 {data.get('share')}, 거리 {data.get('distance')}km, 상태: {data.get('status')}")
    draw("② 세대원 능력", f"{data.get('relation')}, {data.get('age')}세, {data.get('job')}, 경력 {data.get('experience')}, 참여 {data.get('future_plan')}")
    draw("③ 노동력 확보방안", data.get("labor_plan"))
    draw("④ 보유 시설", f"{data.get('owned_name')} {data.get('owned_count')}대 / {data.get('owned_area')}㎡")
    draw("⑤ 계획 시설", f"{data.get('plan_name')} {data.get('plan_count')}대 / {data.get('plan_area')}㎡")
    draw("⑥ 소유 농지", f"{data.get('own_region')} {data.get('own_town')} {data.get('own_lot')} - {data.get('own_crop')} ({data.get('own_area')}㎡, {data.get('own_distance')}km, 자기경영: {data.get('own_self_manage')})")
    draw("⑦ 자금계획", f"자기자금: {data.get('fund_own')}, 차입: {data.get('fund_borrow')}, 총합계: {data.get('fund_total')}")
    draw("⑧ 작물계획", f"{data.get('crop_name')} 착수:{data.get('planting_date')} 수확:{data.get('harvest_date')}")
    draw("⑨ 임차농지", f"{data.get('lease_location')} ({data.get('lease_crop')}, {data.get('lease_area')}㎡, 임차여부: {data.get('lease_status')})")
    draw("⑩ 공유취득 위치", data.get("shared_location"))
    c.save()

def create_agriculture_pdf(data, output_path):
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    x, y = 20 * mm, height - 20 * mm

    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width / 2, y, "농업경영계획서")
    y -= 20
    c.setFont("Helvetica", 11)

    def draw(label, val): nonlocal y; c.drawString(x, y, f"{label}: {val}"); y -= 12

    for i in range(len(data['region'])):
        draw(f"① 취득 대상 농지 {i+1}", f"{data['region'][i]} {data['district'][i]} {data['town'][i]} {data['village'][i]} {data['lot_number'][i]} - {data['area'][i]}㎡, {data['share'][i]}, {data['distance'][i]}km")

    for i in range(len(data['name'])):
        draw(f"② 세대원 {i+1}", f"{data['name'][i]} ({data['relation'][i]}), 나이: {data['age'][i]}, 직업: {data['job'][i]}, 경력: {data['experience'][i]}, 참여계획: {data['future_plan'][i]}")

    draw("③ 노동력 확보방안", data["labor_plan"])

    for i in range(len(data['machine_name'])):
        draw(f"④ 농기계 {i+1}", f"{data['machine_name'][i]} {data['machine_count'][i]}대")
    for i in range(len(data['facility_name'])):
        draw(f"⑤ 시설 {i+1}", f"{data['facility_name'][i]} {data['facility_area'][i]}㎡")

    for i in range(len(data['own_location'])):
        draw(f"⑥ 소유농지 {i+1}", f"{data['own_location'][i]} {data['own_lot'][i]} - {data['own_crop'][i]}, {data['own_area'][i]}㎡, 거리: {data['own_distance'][i]}km")

    draw("⑦ 연고자", f"{data['relative_name']} ({data['relative_relation']})")
    draw("⑧ 자금계획", f"자기자금: {data['own_funds']}원, 차입금: {data['borrowed_funds']}원, 총계: {data['total_funds']}원")

    for i in range(len(data['crop_name'])):
        draw(f"⑨ 재배작물 {i+1}", f"{data['crop_name'][i]}, 착수: {data['planting_date'][i]}, 수확: {data['harvest_date'][i]}, 일정: {data['schedule'][i]}")

    for i in range(len(data['lease_location'])):
        draw(f"⑩ 임차농지 {i+1}", f"{data['lease_location'][i]} ({data['lease_crop'][i]}, {data['lease_area'][i]}㎡, 임차: {data['lease_status'][i]})")

    draw("⑪ 공유취득 설명", data["shared_location_note"])

    c.save()
