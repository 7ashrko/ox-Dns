# PS4 DNS Pro — دليل التثبيت الكامل

## 1) المتطلبات

- VPS بنظام Ubuntu 24.04 LTS أو Debian حديث.
- IPv4 عام ثابت للـVPS.
- معرفة الـPublic IPv4 لشبكة الإنترنت التي يوجد فيها جهاز PS4.
- اتصال SSH بالـVPS.

> ملاحظة: المشروع يستخدم DNS filtering. لا يوجد ضمان أن كل مسار تحديث مستقبلي يمكن منعه بواسطة DNS وحده.

---

## 2) الدخول إلى VPS

من الكمبيوتر:

```bash
ssh root@VPS_IP
```

أو استخدم عميل SSH على الهاتف.

---

## 3) رفع المشروع

ارفع ملف ZIP إلى الـVPS ثم:

```bash
unzip ps4-dns-pro.zip
cd ps4-dns-pro/server
```

إذا لم يكن `unzip` مثبتًا:

```bash
apt update
apt install unzip -y
```

---

## 4) تثبيت DNS

المشروع يستخدم Unbound.

نفّذ:

```bash
sudo HOME_PUBLIC_IP=YOUR_HOME_PUBLIC_IP bash install.sh
```

استبدل:

```text
YOUR_HOME_PUBLIC_IP
```

بالـPublic IPv4 لشبكة المنزل التي يتصل منها الـPS4.

بعد التثبيت:

```bash
systemctl status unbound
```

يجب أن تكون الحالة:

```text
active (running)
```

---

## 5) اختبار DNS

من جهاز داخل شبكة المنزل:

```bash
dig @VPS_IP example.com
```

يجب أن تحصل على إجابة DNS.

اختبار نطاق تحديث موجود في القائمة:

```bash
dig @VPS_IP fus01.ps4.update.playstation.net
```

المتوقع:

```text
status: NXDOMAIN
```

---

## 6) تثبيت لوحة التحكم

من مجلد المشروع:

```bash
cd ps4-dns-pro/server
sudo bash install-ui.sh
```

بعدها:

```bash
systemctl status ps4-dns-ui
```

---

## 7) السماح بالوصول إلى لوحة التحكم

لا تجعل لوحة التحكم مفتوحة للإنترنت كله.

نفّذ:

```bash
sudo ufw allow from YOUR_HOME_PUBLIC_IP to any port 8080 proto tcp
```

ثم افتح:

```text
http://VPS_IP:8080
```

---

## 8) إعداد PS4

في PS4:

Settings
→ Network
→ Set Up Internet Connection

اختر Wi-Fi أو LAN حسب اتصالك.

ثم:

```text
Custom
IP Address Settings: Automatic
DHCP Host Name: Do Not Specify
DNS Settings: Manual
```

ضع:

```text
Primary DNS: VPS_IP
Secondary DNS: VPS_IP
```

ثم:

```text
MTU Settings: Automatic
Proxy Server: Do Not Use
```

واختر:

```text
Test Internet Connection
```

---

## 9) ماذا تفعل لوحة التحكم؟

الواجهة تعرض:

- حالة Unbound.
- عدد قواعد الحجب.
- قائمة Domains.
- إضافة Domain.
- إزالة Domain.
- تحديث إعدادات Unbound تلقائيًا.

القواعد تستخدم:

```text
always_nxdomain
```

أي أن النطاق المحدد يرجع NXDOMAIN بدل عنوان IP.

---

## 10) قائمة الحجب

القائمة موجودة في:

```text
/etc/unbound/ps4-blocklist.conf
```

ولا يجب حذف القواعد الموجودة إلا إذا كنت تعرف سبب ذلك.

لإضافة نطاق يدويًا من الطرفية:

```conf
local-zone: "example.domain" always_nxdomain
```

ثم:

```bash
unbound-checkconf /etc/unbound/unbound.conf
systemctl reload unbound
```

والأسهل استخدام زر Add Domain في لوحة التحكم.

---

## 11) إيقاف الحجب

إذا أردت إعادة PS4 إلى DNS عادي، غيّر DNS في PS4 إلى:

```text
Automatic
```

ولا تحتاج إلى تعديل الجهاز نفسه.

---

## 12) مشاكل شائعة

### DNS لا يعمل

تحقق:

```bash
systemctl status unbound
ss -lntup | grep ':53'
```

ثم:

```bash
ufw status
```

### الواجهة لا تفتح

تحقق:

```bash
systemctl status ps4-dns-ui
ss -lntup | grep ':8080'
```

وتأكد أن Firewall يسمح بعنوان منزلك فقط:

```bash
ufw status numbered
```

### PS4 لا يستطيع الوصول إلى الإنترنت

أعد DNS إلى Automatic مؤقتًا للتأكد أن المشكلة من DNS filtering وليس اتصال الإنترنت.

---

## 13) ملاحظة حول PS4 13.52

المشروع يحتوي على قائمة جاهزة من مضيفات تحديث PS4 المعروفة، لكنه ليس "ضمانًا دائمًا" لإيقاف كل تحديث مستقبلي. Sony قد تغيّر endpoints أو تستخدم مسارات أخرى.

لا تقم بحجب:

```text
playstation.net
```

بالكامل، لأن ذلك قد يؤثر على PSN وتسجيل الدخول وخدمات الألعاب.

---

## 14) الأمان

لا تفتح DNS وواجهة الإدارة للعالم بدون قيود.

الـFirewall في المشروع يقيد DNS إلى Public IP الخاص بشبكتك.

وللوصول البعيد إلى لوحة التحكم، استخدم VPN أو reverse proxy مع authentication بدل فتح المنفذ 8080 للعامة.

---

## 15) أوامر الإدارة السريعة

حالة DNS:

```bash
systemctl status unbound
```

إعادة تشغيل DNS:

```bash
systemctl restart unbound
```

فحص الإعداد:

```bash
unbound-checkconf /etc/unbound/unbound.conf
```

إعادة تحميل القواعد:

```bash
systemctl reload unbound
```

حالة الواجهة:

```bash
systemctl status ps4-dns-ui
```

إعادة تشغيل الواجهة:

```bash
systemctl restart ps4-dns-ui
```

---

## 16) المسارات المهمة

```text
/etc/unbound/unbound.conf
/etc/unbound/ps4-blocklist.conf

/opt/ps4-dns/app/app.py
/opt/ps4-dns/app/templates/index.html
/opt/ps4-dns/app/static/style.css
```
