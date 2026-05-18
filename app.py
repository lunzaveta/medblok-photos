from flask import Flask, request, render_template_string, redirect, url_for
import os
import pg8000.native
from datetime import datetime
from urllib.parse import urlparse

app = Flask(__name__)

DOCTORS = {
    "Урзик ОН": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778758301192-1kc4hgzs.jpg",
    "Рыбалко ТС": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778758316678-xygd8np5.png",
    "Котельникова ВД": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778758332754-epokkels.png",
    "Пономарева ЕА": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778758346573-cjlpgz8h.jpg",
    "Нецветаева АЭ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778758359629-9ae730wu.jpg",
    "Вилисова ЕГ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778758373632-0gi2qnzs.jpg",
    "Вахрамеева ТВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778758387103-wemwfoty.jpg",
    "Титков АВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778758402458-f5vou92r.jpg",
    "Пикунова ЮВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778758417221-5hbtkodk.png",
    "Стрельцова ЕВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778758432427-nw48fqgn.jpg",
    "Якушкина АВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778758447047-f1bg1f3t.jpg",
    "Жарко АС": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778758463522-nvm3el6i.jpg",
    "Мирач ГД": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778758479366-420yfcao.png",
    "Мосолкова ДП": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778758495894-khkpd2me.png",
    "Чиркина АА": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778758512260-mkrkofvv.png",
    "Кутузова ЛС": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778758527706-8mwtvmga.png",
    "Геренюк ИВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778758542675-8vbk35zr.png",
    "Донченко ДБ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778758556509-0z5pzvau.png",
    "Эра МС": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778758574971-15ssje71.jpg",
    "Неверов ВЕ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778758590934-vnj2o4rz.jpg",
    "Чеканова ЕВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778758609830-2uxqgozo.jpg",
    "Еремина АН": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778758629506-gj6iak3y.jpg",
    "Хардина ИА": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778758643639-wfjpcccl.jpg",
    "Постникова ЛН": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778758669071-hersyb16.png",
    "Гилязова ДК": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778758690082-7a5xjszn.jpg",
    "Велиметова АО": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778758715965-57zqh9e8.jpg",
    "Макеева ЯЮ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778758735444-vo55ruij.jpg",
    "Сельчук ВМ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778758753195-dueigk6g.jpg",
    "Лапенко ТА": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778758769304-pfu4ciy8.png",
    "Гогина АЕ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778758782919-xtddwaz6.jpg",
    "Полушкина МА": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778758797539-0rsqonzb.png",
    "Даукараева ЮВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778758811954-qnueostj.jpg",
    "Гросс АВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778758825485-5v3b2m09.png",
    "Закатей ВМ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778758843185-i88t9nz3.png",
    "Храмова КП": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778758861055-llx65co8.png",
    "Пашаева ЛФ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778758876152-qfn464t3.png",
    "Оборская ЕА": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778758892472-sbpmxc22.png",
    "Сазонов ПА": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778758906689-t70en2ez.jpg",
    "Гнедов ГВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778758922387-8mj2k1j7.png",
    "Новицкая ЕВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778758939808-q8qq7oig.jpg",
    "Попова ДП": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778758954948-fup1sn48.png",
    "Клевова НС": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778758973311-wpevvw23.png",
    "Шутова АА": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778758993755-t7wq2nsv.jpg",
    "Пастухова АВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778759013172-simp8nx4.jpg",
    "Кочетков НА": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778759026844-35sdqqtn.jpg",
    "Ларина ДА": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778759042846-22r98lsh.png",
    "Греков ИИ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778759063235-6jy7c53s.png",
    "Лубяницкая ЮО": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778759079108-l6h2vftp.png",
    "Журавлева ОА": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778759096197-zz96kf5t.png",
    "Кондрашова ЕА": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778759113262-vawo6cme.jpg",
    "Трунина ТН": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778759127890-31itxmwa.jpg",
    "Зимина АВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778759141477-fxfy5w3i.jpg",
    "Гернер ОЛ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778759157535-128yschd.png",
    "Голубева ЮО": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778759173037-88mqnkby.jpg",
    "Амиров АА": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778759187138-hp0le8ue.png",
    "Тихонова МВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778759207151-ycco5foy.jpg",
    "Вавель АЛ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778759226705-qminc12p.jpg",
    "Быстрых ЕВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778759242748-ngcal2e9.jpg",
    "Богомолова ИВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778759259572-krkunwrz.jpg",
    "Першина МА": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778759275741-w3spfb6f.png",
    "Семенова ЕЮ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778759291864-bg81selx.png",
    "Кривопляс МВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778759308359-bvymz1d4.png",
    "Таранова ВА": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778759324525-zui1gyal.jpg",
    "Фомченко СГ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778759339336-gr5xmwb6.jpg",
    "Вострякова МН": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778759354554-rio5cldg.jpg",
    "Литвинова АА": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778759370065-gebouef7.png",
    "Кодельник ММ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778759386698-reosk9k6.png",
    "Нецепляева МГ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778759401768-0ccvlr5x.jpg",
    "Дивейкина АЮ": "",
    "Букуева СС": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778759417381-wprrm2ny.png",
    "Веселова НА": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778759433579-9kefyh1k.png",
    "Ящук ДР": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778759449361-py15x0uw.png",
    "Воронцова ЛВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778759466440-qve0ih2l.png",
    "Рожкова ВС": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778759480583-6ivxrv4q.jpg",
    "Ильичев АВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778759503957-85twu222.png",
    "Храмушина ЕН": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778759520285-ijjeogh7.png",
    "Беглова НЮ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778759532057-x8266k4p.jpg",
    "Елисеева НВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778759551762-gcmznge7.jpg",
    "Яковлева ОЮ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778759567301-12o9nlwb.png",
    "Гайворонская АМ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778759589442-7wiaqe2t.jpg",
    "Коваленко АВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778759609634-vlkcdvok.jpg",
    "Давыдов ДА": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778759625240-i1dphk0l.jpg",
    "Муленкова ИГ": "",
    "Вершина НВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778759650943-3dldty5l.png",
    "Злобина ИА": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778759671461-daj91jwi.jpg",
    "Сафронов ВВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778759695418-v14zvgm7.jpg",
    "Синотова МВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778759710082-xnq1husq.jpg",
    "Воронова ВИ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778759726397-cuhtbnex.png",
    "Лопан КВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778759762961-kllk1nqh.jpg",
    "Петренко АМ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778759778429-adtabboa.png",
    "Зверева МА": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778759796911-0v3n8g5p.jpg",
    "Савенко ВД": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778759815875-6rc36v7p.jpg",
    "Жукова СВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778759829627-nqczkfly.jpg",
    "Прокушев ТА": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778759844365-q0xxs5os.png",
    "Дашко ГЮ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778759865044-88y5oxhl.jpg",
    "Варламова ДА": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778759879336-zqxx236j.png",
    "Архипова ЕЕ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778759894953-7ytn1z3t.jpg",
    "Панина АА": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778759910213-9uo9c55t.png",
    "Сергеенко МА": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778759934036-63phf4n8.jpg",
    "Николаева АС": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778759948181-zcfr9x9u.png",
    "Малышева КВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778759961380-b4uo9edu.jpg",
    "Суренкова ДА": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778759975832-c32vcem1.png",
    "Лебедева АФ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778759992747-jxk3e5vp.png",
    "Биешева АВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778760007765-igjonou5.jpg",
    "Миронова АА": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778760023565-97nkng65.png",
    "Федорченко АВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778760040291-erip9q3c.png",
    "Голышева МФ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778760055042-hdr7y7k0.png",
    "Кислица НВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778760069869-kipaa8d9.jpg",
    "Савченкова ЮВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778760086301-eic2tmpz.jpg",
    "Малых ИБ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778760100484-3yqlmnag.png",
    "Ершова ИС": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778760117420-ot5piie9.png",
    "Аладина ГС": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778760131812-tauxm4k3.png",
    "Неверова ЕВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778760149981-u2jfpyz7.png",
    "Яковлева ЛИ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778760170918-r9n28u2k.jpg",
    "Панкратова ЕИ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778760186138-97dfn6wc.png",
    "Чуйкова МН": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778760201752-iejggf04.png",
    "Саранчина ЕВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778760218894-1jlxfxt7.png",
    "Сидельникова ЛР": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778760234942-nuxb53kn.png",
    "Лунеко АИ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778760251040-u9tpx3uh.png",
    "Рыбальченко ЕВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778760268739-5i9cgziv.jpg",
    "Полякова АС": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778760287765-nvx8n76v.jpg",
    "Авраменко ВВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778760302744-odkolq4k.jpg",
    "Капитонова ЛП": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1778760318417-q6eavlmn.png",
    "Ханнанова ФР": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779106462802-ftyf988k.jpg",
    "Васильева ИИ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779106475584-7epqp8sw.png",
    "Григорьева-Домашняя ДД": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779106490406-8bxwbysv.png",
    "Стельмахова ДА": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779106518278-676t9poq.png",
    "Галанцева АВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779106533839-bdmdt84m.png",
    "Покусаева МА": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779110131124-6n8pz8ss.jpg",
    "Идрисова ВА": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779106562560-6uwe3zvp.jpg",
    "Давыдова МА": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779106574377-3o2favxk.jpg",
    "Курешова АВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779106590111-elew9t5g.png",
    "Корочанская АА": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779106618904-xmu0ro0l.jpg",
    "Баранова АА": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779106633138-knkmunku.png",
    "Иванова НД": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779106645929-u34d5s2n.jpg",
    "Колосова ИИ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779106661116-gpzqzm8c.jpg",
    "Осина АИ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779106676693-84j3x6b7.png",
    "Субботина ЮВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779106692829-qx2w4bi1.jpg",
    "Столетова НК": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779106709841-n29l91c6.png",
    "Панферова КА": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779106724561-g658md00.jpg",
    "Карпова МЮ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779106738388-69bg5do1.png",
    "Гусельникова АС": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779106753471-remuppxp.png",
    "Ломоносова СА": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779106768911-qdruktch.png",
    "Макаровская ЕА": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779106782605-78d31dxy.jpg",
    "Пегушина НВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779106797465-3ehz69cs.png",
    "Стороженко АВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779106812406-ggd0y1tl.png",
    "Манахова ОС": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779106825206-x6vkaayx.jpg",
    "Твердовская АВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779106837643-5qv1bchb.jpg",
    "Кладко ЕС": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779106851849-h6l5ctea.png",
    "Гринева АН": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779106867929-1wpgwmk0.jpg",
    "Скотникова ДС": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779106881035-amwljtrh.jpg",
    "Горюнова АА": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779106894826-cpcw5lmm.jpg",
    "Гласс ЕИ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779106908657-bd08woon.jpg",
    "Черкашина АЕ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779106923528-zgotysin.png",
    "Приблуда АВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779106935907-5462plx4.png",
    "Савельева ЕА": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779106950997-mexokqx2.jpg",
    "Краузе КА": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779110170636-y8bl8ibk.jpg",
    "Щеглова АВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779106985843-91or7gnd.png",
    "Белоусов ЮА": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779106998515-gdhpy32d.jpg",
    "Белогородская АЕ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779110260234-aeytm8k2.jpg",
    "Першина НА": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779110313213-oaycrg5v.png",
    "Данилова ПС": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107052342-v5q9ttm6.png",
    "Лазуто ЯВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107065698-63qfdw00.png",
    "Бойко ТВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107080236-ra51nvyi.jpg",
    "Фещенко ЕМ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107095628-9yw2xsbb.png",
    "Надбитова АА": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107108663-yz82jgzp.jpg",
    "Крухмалева АВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107122901-jcudfu7b.jpg",
    "Заметалина ИВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107138119-6bn7876h.png",
    "Юдичева ПБ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107152696-h2jduz12.png",
    "Кисленкова АЮ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107168218-ctiwfoql.png",
    "Макаренко АГ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107181140-60xp3wbh.jpg",
    "Мозалевская ЕН": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107196184-g2qmk9mw.png",
    "Крушкова ЕМ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107210812-rulcucbm.jpg",
    "Шуда СВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107224302-ne5aejr9.jpg",
    "Багдасарьян ОВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107239275-b2dhr33w.png",
    "Макаренко ОА": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107267832-qnoa90gk.png",
    "Давыдова АВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107283487-1qadujhj.png",
    "Анаевский КЕ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107297014-wdq08kf2.jpg",
    "Кулешова АВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107312707-otgsoc9d.jpg",
    "Пырх ТВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107327591-zfuxaiwb.png",
    "Мокина АР": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107342697-pz6lkphr.png",
    "Минова АВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107357487-ie6y3nb2.png",
    "Бабенко ВВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107375816-qgy3nkvd.png",
    "Спиридонова НН": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107391666-06cb4bes.png",
    "Грязина НГ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107406083-508vsnjj.jpg",
    "Бариева ДС": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107421381-qaajjon6.jpg",
    "Бочкарёва НВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107438708-hm3whv4y.png",
    "Голикова СВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107454149-27n4kl6m.png",
    "Воропаева НЮ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107471959-yvbdfnld.png",
    "Джамалова АЗ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107488035-s9heq0lm.jpg",
    "Проскурякова ТВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107501075-gjkrtvy0.jpg",
    "Яковлева ЕВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107523302-8h46hx40.png",
    "Шайтанюк АВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107543155-5df7m9p5.jpg",
    "Колоколкина ОА": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107559830-0ml71ikc.png",
    "Слюсарева ЯН": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107577904-b0j2i43j.jpg",
    "Чуб ВВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107593634-8czm1wqy.jpg",
    "Шибакова ЕС": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107609001-kl544nam.png",
    "Белов АА": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107627555-nu72umpm.jpg",
    "Казакова ВС": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107639735-p11u7705.jpg",
    "Васильев ВВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107654500-bir8bh23.png",
    "Моторина МА": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107671432-tx237h0h.png",
    "Коваленко МА": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107685706-p5hpfd6q.jpg",
    "Белая ДВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107698426-nsdfy3lj.png",
    "Павлова ИС": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107718458-fx7fr7in.png",
    "Пежемская АИ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107732314-06q6lpta.jpg",
    "Рассказов ДВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107745952-3tj6pwnv.jpg",
    "Горшкова ОМ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107779153-8d7obfpw.png",
    "Контанистова ВВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107793163-6a5wlmav.jpg",
    "Павлищак ОВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107806755-zdfilf0o.png",
    "Васильева ОС": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107820507-o4k83k5n.jpg",
    "Лягина ИС": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107841292-zn3kh7di.png",
    "Иванова КБ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107855640-vif0yb6j.png",
    "Бакина АЮ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107868182-lc2n0tun.jpg",
    "Королёва ЮВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107881227-k8kvzakr.jpg",
    "Липартиани ММ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107898706-th7w66v4.jpg",
    "Болдырева ЮГ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107911620-s78pq52h.jpg",
    "Романова ОА": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107924661-sz7fga93.jpg",
    "Щепетильникова АС": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107938806-qqa7qp7b.jpg",
    "Русанова ОК": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107954319-hc3n9ww4.jpg",
    "Настаева МФ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107967888-wz3b8qvj.jpg",
    "Лунев ДС": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107981771-mrn9xspk.png",
    "Есина ИВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779107995673-i8jo1t9t.jpg",
    "Колемасова АН": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779108008193-s9xebdna.jpg",
    "Мясищева ТА": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779108021015-mvwgwj99.png",
    "Есипова КМ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779108034510-o7p8qv8w.png",
    "Маухина ПС": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779108048290-4na4cub2.png",
    "Гуськова ЕА": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779108067072-zto4myoa.png",
    "Рафикова НД": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779108081400-11wjdhbm.png",
    "Герасимова АИ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779108093997-53ewoato.jpg",
    "Савченко АГ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779108107655-bl305fuj.jpg",
    "Целовальникова ТС": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779108122205-c2i8rb79.png",
    "Климова МЛ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779108135147-y04242cb.jpg",
    "Плотникова ВА": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779108147928-qh64htdp.jpg",
    "Насонова АД": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779108163600-luxr21r1.jpg",
    "Колоскова КВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779108177506-s0bc9a2d.png",
    "Гусева ЕА": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779108192058-hu1jpwft.jpg",
    "Зейля АС": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779108204366-3u7ccdj2.jpg",
    "Гончарова ДМ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779108219266-azhbbidd.png",
    "Степичева ТС": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779108232658-0pxck5sq.jpg",
    "Пахомова ЕА": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779108248630-tkk10fj0.png",
    "Абрамова ВЛ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779108262514-s47jdz5j.jpg",
    "Гречушникова ЛИ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779108277139-wzxgfgge.jpg",
    "Мельчакова ЕА": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779108291120-8i24dzep.jpg",
    "Клейн КВ": "https://s3.ru1.storage.beget.cloud/8b03d143f59e-daring-viola/doctor-processed/1779108305430-a8od88nb.png"
}
STATUS_LABELS = {
    "approve": "✅ Нравится",
    "edit":    "✏️ Нужны правки",
    "decline": "❌ Отказываюсь от размещения",
}

def get_db():
    u = urlparse(os.environ["DATABASE_URL"])
    return pg8000.native.Connection(
        user=u.username, password=u.password,
        host=u.hostname, port=u.port or 5432,
        database=u.path.lstrip("/"), ssl_context=True
    )

def init_db():
    conn = get_db()
    conn.run("""CREATE TABLE IF NOT EXISTS responses (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        status TEXT NOT NULL,
        label TEXT NOT NULL,
        comment TEXT DEFAULT '',
        timestamp TIMESTAMP DEFAULT NOW()
    )""")
    # Add comment column if not exists (for existing tables)
    try:
        conn.run("ALTER TABLE responses ADD COLUMN IF NOT EXISTS comment TEXT DEFAULT ''")
    except:
        pass
    conn.close()

def save_response(name, status, comment=""):
    conn = get_db()
    conn.run("INSERT INTO responses (name, status, label, comment) VALUES (:n, :s, :l, :c)",
             n=name, s=status, l=STATUS_LABELS.get(status, status), c=comment)
    conn.close()

def already_responded(name):
    conn = get_db()
    rows = conn.run("SELECT 1 FROM responses WHERE name = :n LIMIT 1", n=name)
    conn.close()
    return len(rows) > 0

BASE_STYLE = """
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<link href="https://fonts.googleapis.com/css2?family=Unbounded:wght@400;600&family=Inter:wght@300;400;500&display=swap" rel="stylesheet">
<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
:root { --bg: #0f1117; --surface: #1a1d27; --border: #2a2d3a; --text: #e8eaf0; --muted: #6b7280; --accent: #4f8ef7; }
body { background: var(--bg); color: var(--text); font-family: 'Inter', sans-serif; min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 24px; }
.card { background: var(--surface); border: 1px solid var(--border); border-radius: 16px; padding: 40px; width: 100%; max-width: 480px; animation: fadeUp .4s ease both; }
@keyframes fadeUp { from { opacity: 0; transform: translateY(16px); } to { opacity: 1; transform: translateY(0); } }
.logo { font-family: 'Unbounded', sans-serif; font-size: 13px; font-weight: 600; letter-spacing: .08em; color: var(--accent); text-transform: uppercase; margin-bottom: 32px; }
h1 { font-family: 'Unbounded', sans-serif; font-size: 20px; font-weight: 600; line-height: 1.3; margin-bottom: 8px; }
p.sub { color: var(--muted); font-size: 14px; line-height: 1.6; margin-bottom: 28px; }
label { display: block; font-size: 12px; font-weight: 500; color: var(--muted); text-transform: uppercase; letter-spacing: .06em; margin-bottom: 8px; }
input[type="text"] { width: 100%; background: var(--bg); border: 1px solid var(--border); border-radius: 10px; color: var(--text); font-family: 'Inter', sans-serif; font-size: 16px; padding: 14px 16px; outline: none; transition: border-color .2s; }
input[type="text"]:focus { border-color: var(--accent); }
textarea { width: 100%; background: var(--bg); border: 1px solid var(--border); border-radius: 10px; color: var(--text); font-family: 'Inter', sans-serif; font-size: 14px; padding: 12px 16px; outline: none; transition: border-color .2s; resize: vertical; min-height: 80px; margin-top: 16px; }
textarea:focus { border-color: var(--accent); }
textarea::placeholder { color: var(--muted); }
.btn-primary { display: block; width: 100%; margin-top: 16px; padding: 14px; background: var(--accent); color: #fff; font-family: 'Inter', sans-serif; font-size: 15px; font-weight: 500; border: none; border-radius: 10px; cursor: pointer; transition: opacity .2s; }
.btn-primary:hover { opacity: .88; }
.photo-wrap { border-radius: 12px; overflow: hidden; margin-bottom: 28px; border: 1px solid var(--border); background: var(--bg); aspect-ratio: 3/4; display: flex; align-items: center; justify-content: center; }
.photo-wrap img { width: 100%; height: 100%; object-fit: cover; display: block; }
.actions { display: flex; flex-direction: column; gap: 10px; }
.btn-action { display: flex; align-items: center; gap: 12px; padding: 14px 18px; border-radius: 10px; border: 1px solid var(--border); background: var(--bg); color: var(--text); font-family: 'Inter', sans-serif; font-size: 15px; cursor: pointer; transition: border-color .2s, background .2s; text-align: left; width: 100%; }
.btn-action:hover { border-color: var(--accent); background: rgba(79,142,247,.07); }
.btn-action.selected { border-color: var(--accent); background: rgba(79,142,247,.12); }
.btn-action .icon { font-size: 18px; flex-shrink: 0; }
.error { background: rgba(239,68,68,.1); border: 1px solid rgba(239,68,68,.3); border-radius: 10px; padding: 12px 16px; font-size: 14px; color: #fca5a5; margin-top: 14px; }
.hint { font-size: 12px; color: var(--muted); margin-top: 8px; }
.doctor-name { font-size: 12px; color: var(--muted); margin-bottom: 20px; }
.doctor-name span { color: var(--accent); font-weight: 500; }
.comment-block { display: none; margin-top: 16px; }
table { width: 100%; border-collapse: collapse; font-size: 13px; margin-top: 20px; }
th, td { padding: 10px 12px; text-align: left; border-bottom: 1px solid var(--border); }
th { color: var(--muted); font-weight: 500; }
</style>"""

ENTER_HTML = """<!DOCTYPE html><html><head>""" + BASE_STYLE + """<title>Медблок</title></head><body>
<div class="card"><div class="logo">Медблок</div><h1>Согласование фотографии</h1>
<p class="sub">Введите вашу фамилию и инициалы, чтобы увидеть фото для размещения.</p>
<form method="POST" action="/photo">
<label for="name">Фамилия и инициалы</label>
<input type="text" id="name" name="name" placeholder="Например: Иванова НД" autocomplete="off" autofocus>
<div class="hint">Формат: Фамилия ИО (без точек)</div>
{% if error %}<div class="error">{{ error }}</div>{% endif %}
<button type="submit" class="btn-primary">Продолжить →</button>
</form></div></body></html>"""

PHOTO_HTML = """<!DOCTYPE html><html><head>""" + BASE_STYLE + """<title>Медблок</title></head><body>
<div class="card"><div class="logo">Медблок</div><h1>Ваше фото</h1>
<p class="sub">Рассмотрите фотографию и выберите решение.</p>
<div class="doctor-name"><span>{{ name }}</span></div>
<div class="photo-wrap"><img src="{{ image_url }}" alt="Ваше фото" onerror="this.style.display='none'"></div>
<form method="POST" action="/respond" id="form">
<input type="hidden" name="name" value="{{ name }}">
<input type="hidden" name="status" id="status-input" value="">
<div class="actions">
  <button type="button" onclick="selectStatus('approve', this)" class="btn-action"><span class="icon">✅</span> Да, нравится — можно размещать</button>
  <button type="button" onclick="selectStatus('edit', this)" class="btn-action"><span class="icon">✏️</span> Нужны правки</button>
  <button type="button" onclick="selectStatus('decline', this)" class="btn-action"><span class="icon">❌</span> Отказываюсь от размещения</button>
</div>
<div class="comment-block" id="comment-block">
  <textarea name="comment" placeholder="Напишите комментарий (необязательно)..."></textarea>
</div>
<button type="submit" class="btn-primary" id="submit-btn" style="display:none;">Отправить ответ →</button>
</form>
<script>
function selectStatus(status, btn) {
  document.querySelectorAll('.btn-action').forEach(b => b.classList.remove('selected'));
  btn.classList.add('selected');
  document.getElementById('status-input').value = status;
  document.getElementById('submit-btn').style.display = 'block';
  var cb = document.getElementById('comment-block');
  cb.style.display = (status === 'edit' || status === 'decline') ? 'block' : 'none';
}
</script>
</div></body></html>"""

DONE_HTML = """<!DOCTYPE html><html><head>""" + BASE_STYLE + """<title>Медблок</title></head><body>
<div class="card" style="text-align:center;"><div class="logo">Медблок</div>
<div style="font-size:48px;margin-bottom:20px;">{{ icon }}</div>
<h1>{{ title }}</h1><p class="sub" style="margin-top:10px;">{{ message }}</p>
</div></body></html>"""

ALREADY_HTML = """<!DOCTYPE html><html><head>""" + BASE_STYLE + """<title>Медблок</title></head><body>
<div class="card" style="text-align:center;"><div class="logo">Медблок</div>
<div style="font-size:48px;margin-bottom:20px;">🔒</div>
<h1>Ответ уже принят</h1>
<p class="sub" style="margin-top:10px;">Вы уже отправили решение. Если нужно изменить — свяжитесь с администратором.</p>
</div></body></html>"""

ADMIN_HTML = """<!DOCTYPE html><html><head>""" + BASE_STYLE + """<title>Медблок — Админ</title></head><body>
<div class="card" style="max-width:900px;"><div class="logo">Медблок — Ответы</div>
<h1>Результаты согласования</h1>
<p class="sub">Всего ответов: {{ total }}</p>
<table><tr><th>ФИО</th><th>Статус</th><th>Комментарий</th><th>Дата</th></tr>
{% for row in rows %}<tr><td>{{ row[0] }}</td><td>{{ row[1] }}</td><td>{{ row[2] or "—" }}</td><td>{{ row[3] }}</td></tr>{% endfor %}
</table></div></body></html>"""

@app.route("/", methods=["GET"])
def index():
    return render_template_string(ENTER_HTML, error=None)

@app.route("/photo", methods=["POST"])
def photo():
    name = request.form.get("name", "").strip()
    if not name:
        return render_template_string(ENTER_HTML, error="Введите фамилию и инициалы.")
    if name not in DOCTORS:
        return render_template_string(ENTER_HTML, error="Не найдено. Проверьте формат: Иванова НД (без точек).")
    if already_responded(name):
        return render_template_string(ALREADY_HTML)
    return render_template_string(PHOTO_HTML, name=name, image_url=DOCTORS[name])

@app.route("/respond", methods=["POST"])
def respond():
    name = request.form.get("name", "").strip()
    status = request.form.get("status", "").strip()
    comment = request.form.get("comment", "").strip()
    if not name or name not in DOCTORS or status not in STATUS_LABELS:
        return redirect(url_for("index"))
    if already_responded(name):
        return render_template_string(ALREADY_HTML)
    save_response(name, status, comment)
    messages = {
        "approve": ("✅", "Спасибо!", "Ваше согласие зафиксировано. Фото будет размещено."),
        "edit":    ("✏️", "Принято!", "Мы получили запрос на правки. Скоро свяжемся с вами."),
        "decline": ("❌", "Принято!", "Отказ зафиксирован. Фото размещено не будет."),
    }
    icon, title, message = messages[status]
    return render_template_string(DONE_HTML, icon=icon, title=title, message=message)

@app.route("/admin")
def admin():
    conn = get_db()
    rows = conn.run("SELECT name, label, comment, to_char(timestamp, 'DD.MM.YYYY HH24:MI') FROM responses ORDER BY timestamp DESC")
    conn.close()
    return render_template_string(ADMIN_HTML, rows=rows, total=len(rows))

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
