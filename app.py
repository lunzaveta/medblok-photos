from flask import Flask, request, render_template_string, redirect, url_for
import os
import pg8000.native
from datetime import datetime

app = Flask(__name__)

DOCTORS = {
    "Урзик ОН": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/3Hx3oXxvOXQZYtuaXZU5BTlhGbMRgunRoF3qxB4m.png",
    "Рыбалко ТС": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/tp8sGrAI8EsmcbiqH1vShcVgR49Pw5dTjZSKBJUr.png",
    "Котельникова ВД": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/ls3KaHaHKGlSTuSZbrv3BRR2h1wo14.jpg",
    "Пономарева ЕА": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/llcMYGnKt0ygiTB0yhVRvm51KtX6jc.png",
    "Нецветаева АЭ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/a4t4RgKf5CHSu26WYI0fPxAqVJOVDo.png",
    "Вилисова ЕГ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/4NAwgIrpAfxzUNMXDnkkOKZAECw7vXVO48Tp1QW0.jpg",
    "Вахрамеева ТВ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/bbT1bctXFeh6OrrArK8qmKtegiDvDb.png",
    "Титков АВ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/IcjFJOsN4s3t7OdwLuIQ5vEJeFGB1oKbMeXWkohf.jpg",
    "Пикунова ЮВ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/HHDRZytAWpU9LyriXagrddnvdPtEue.png",
    "Стрельцова ЕВ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/cVtv2C6LKDfXE4t71iEAo1WPvGQkcd.png",
    "Якушкина АВ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/1LDpiyIsmYvWdIqQfALzUCoaR96zky.png",
    "Жарко АС": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/FXHZwWWQbOTK2SSD4mj1CQj8S1fGyI.png",
    "Мирач ГД": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/UIIAITxaKDEoKAhza6rqUcv3DNDY2C.png",
    "Мосолкова ДП": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/TUDsiMtDSmx8f6wZwWUucF4PUzV7pq.png",
    "Чиркина АА": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/zMkIFWdNYpEM14n5g55eDtygex4DOZ.jpg",
    "Кутузова ЛС": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/XkF2GDM6h5FPwRDyCauwTVi8ev34vg.png",
    "Геренюк ИВ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/K7vdF5ur0ZLETeiusahok2hGZ2rbFy.jpg",
    "Донченко ДБ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/kpr5dtl13mDY6LHIo9eZ9hBe2Nq20W.png",
    "Эра МС": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/Q0g4aW1NaTORwlNANchCS6wl9W4ROD.png",
    "Неверов ВЕ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/9NeDI9qFylSfVmuloK2KP3HyqB8jcj.png",
    "Чеканова ЕВ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/ZLSEIPlcGXc9TNHgFyTIvQhGEe84ks.jpg",
    "Еремина АН": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/IGHFSdLvHuLN4h4Bew4UarwVnDZUkY.png",
    "Хардина ИА": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/5QL5QaTJb3O8CobrlyhdcUJzQchpUd.png",
    "Постникова ЛН": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/x9KlpL3097w4OFGk3UwD8yM55LSw5L.png",
    "Гилязова ДК": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/kc6smFVvZtQhzzSgMq5mpVs9rL6Bsb.jpg",
    "Велиметова АО": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/a9725yXnculDWeKAlu50OQEG4j22th.png",
    "Макеева ЯЮ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/iLjxswku5ptEohA4gnsgVdWRs6GLjs.jpg",
    "Сельчук ВМ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/sT6HGYxwj0Hu0hAG6PWN0B4TbrmO6s.jpg",
    "Лапенко ТА": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/lP09oqpJrMSbYPTCglK6NVZukyDY9J.png",
    "Гогина АЕ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/2nkbxknkg7iZBDV8foLZkJwDJCc5Uc.png",
    "Полушкина МА": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/KLH6o2iuVNOh7sj8sFwTCVEHZ2dVVG.jpg",
    "Даукараева ЮВ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/TNf3eV98z0nh6bTYWddSRRUBBIEPa2J0BNWcbBVv.jpg",
    "Гросс АВ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/7Jgs1MobhBNmtPdfhIj31k6qpRTNTSegYINKOQmQ.jpg",
    "Закатей ВМ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/Pj8MaPL5GdufRz7o6QKHGJoqHtEtU1.png",
    "Храмова КП": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/ho05NZSYWbpEBfq59Uu0FGB9f3Ev2d.png",
    "Пашаева ЛФ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/AxEcplrLJeiEl2pEAXpzIywxYWBCKv.jpg",
    "Оборская ЕА": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/vHlN87gV8OIRbIrGs6KQsipnVarmhn.png",
    "Сазонов ПА": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/zyCtJuhE40eI6KA5B8EF6sCcvo6vWT.png",
    "Гнедов ГВ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/jRgrQYpP76jBYxNDJcGZqxWEF5BUMo.jpg",
    "Новицкая ЕВ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/sFpFpY8uhyx477P9agRGIxVdDwZdSJ.png",
    "Попова ДП": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/U1WPkTtmTHvVEpTJqBOkge67wF2dM4.png",
    "Клевова НС": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/PFR6orIrBrLrneVKj1XH4aSyrYajtp.png",
    "Шутова АА": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/xBsThYzep1H7xsRBHcV4IRaLMvrTlLkxd146KAoC.png",
    "Пастухова АВ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/DOQO2iPO9r88r9Br1CifDOMAVm1o65.jpg",
    "Кочетков НА": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/Q5gozVShXCXyVyxfwIgmlmWBdbxC9p.png",
    "Ларина ДА": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/dFx6UYlUHfJYqdktrkErYo6vTKqs9thVmEhWk6ly.jpg",
    "Греков ИИ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/4fVMx6qwJUSVEFb69wTJw8QTWKCFMi.png",
    "Лубяницкая ЮО": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/l9dWLVOgw9U9OftH0n6JYV9AEtW4Vx.png",
    "Журавлева ОА": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/kLKMMR5ZphgJtXSc8dVwzHfckayjZQ.png",
    "Кондрашова ЕА": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/NJiGdbEA55LwNUXvRjJ4yNdvKfH251.jpg",
    "Трунина ТН": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/8t8QcVjci0WsH1O0dJzQvtDq2YF7IC.png",
    "Зимина АВ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/7w89o5Bxdtv4IBMIrgmyWx19N3tSAV.png",
    "Гернер ОЛ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/3Ygbm39k6d3IljAbnb0CM6w06Uhtea.png",
    "Голубева ЮО": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/cn2KkhNqo2KXntb2OJGeZrG64vPBml.png",
    "Амиров АА": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/Npnvk4HrOCic4n9ntwR6Pmj1A6MbyE.png",
    "Тихонова МВ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/q1OvXvEf3Ob1oqtKL7UCSHnn0UuhgX.png",
    "Вавель АЛ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/jrjUQXUIOcxdo1UcpfZaHScPV7j1yB.jpg",
    "Быстрых ЕВ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/jX2ZVa1Eaes7Qe4Zw97LzZbaoi5E4d.png",
    "Богомолова ИВ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/TuCeLIRHvblEoxXiVZjP7NqJNDJiBD.png",
    "Першина МА": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/IrpRSCKEAWFBptmEOKKwsyGQtPk4q4.png",
    "Семенова ЕЮ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/DSUa4g5rJFIgZ2BSk9ynFuN5nbkPNifVh3r5lqEI.jpg",
    "Кривопляс МВ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/jfMTDMbwgzduf5nP20aDOVjrqhzojE.jpg",
    "Таранова ВА": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/H7rfKrfx1bppcxWHH2jOhALMETEwJJ.png",
    "Фомченко СГ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/rIkIWKwaWAeZcwc2TTBKlDLMmpJ3Jt.png",
    "Вострякова МН": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/uHw3sfjk4n4YkNnU5yiLqVq9bP9yJ3.jpg",
    "Литвинова АА": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/jAz5bYMxXknvEcx9tvxcvDE6pezUz3C6VPDgryFa.jpg",
    "Кодельник ММ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/1YiObDDnGmbY1deWlLtGcXhFxgYVlZ.jpg",
    "Нецепляева МГ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/TXch4nXYpiBVYfs8NjAyaVVXbXuRzf.png",
    "Дивейкина АЮ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/wMzkkPOWs1nJR9PCmG7OSzNtJERUNU.jpg",
    "Букуева СС": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/pBZmBlGPYkZfxDNIa9WwqLgGYIIURl.png",
    "Веселова НА": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/N92tXnrkKHGjqR4eM4zxRSBPtfhKD9.png",
    "Ящук ДР": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/7RwgRP3pE93ESHuNJJtUXYBshwC0Aj.png",
    "Воронцова ЛВ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/j3CRmVs2NWc8vIL2JvPMRjEbnqga7j.jpg",
    "Рожкова ВС": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/eKL453sdLnDzmuYHZWeOw2rY7ZRwdI.jpg",
    "Ильичев АВ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/WQCpfx3NC01UDxPWFmcI7nrAfRo33oXt9InCZG6g.png",
    "Храмушина ЕН": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/3GQkr8igU55el2BiSp5RCOsOjrIZBL.jpg",
    "Беглова НЮ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/7hjTcr94eCufqGx5zWHSLSZtO4sTyB.jpg",
    "Елисеева НВ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/8TolUmpRL4oQ51G32lroJb9GLCL9qm.png",
    "Яковлева ОЮ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/Rbxbf5s041bdsJXhW6uENFzqLhXLNX.png",
    "Гайворонская АМ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/dLQrZ71maVCb5btbUrJwhk4gOT3zky.png",
    "Коваленко АВ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/pYPAtS00D0ud9cJZyaG4z3WXzVaUDm.png",
    "Давыдов ДА": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/Nqw9EYSFrrg9l5HZuKrhb9h1zR7Ivy.png",
    "Муленкова ИГ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/auO9itIJVSRxP8Ytmg5V7laL4Ecu3N2l80KYSI1g.jpg",
    "Вершина НВ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/OxMkLksnFzFf5zuBD3JNNpY5Wvz6xQ.png",
    "Злобина ИА": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/CAJ2vsV4XjDYzHftfhKjRmNvwEqVtZ.png",
    "Сафронов ВВ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/rdD2utZs62gyxEXukWo1FmsOYkk2VW.jpg",
    "Синотова МВ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/00uG3tIuurKhr1479DHfYR24YICDlA.png",
    "Воронова ВИ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/XjxeGxyEsmBWEm5u5xCute4StBEBim.png",
    "Лопан КВ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/8pjjVvIJt2U6xRn6Y0HZQQt4lK6wgC.png",
    "Петренко АМ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/sucNJL2PpNoJzKIgykMvZL8QeuwS11.png",
    "Зверева МА": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/QTUe3p0Q35ghGx4kIxq1Gwu9OWD3iP.png",
    "Савенко ВД": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/ij6ePF3Rp9MVUSIKAzzMacaNWvvVvI.jpg",
    "Жукова СВ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/w0yjYEWZMpmWnQLqA3vmD7seELgJ4h.jpg",
    "Прокушев ТА": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/DbClZfYToYnEw8vU5Dm0zigA7csg15.png",
    "Дашко ГЮ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/84zcWBLWq0WSPKNnxdM2OUCr9o7ESo.png",
    "Варламова ДА": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/xaIjAvYh90bfI9TtYQ9LEVW4tUa72s.png",
    "Архипова ЕЕ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/FnqPLWYHtYSzyJX0wkTK61DBsTDqKv.png",
    "Панина АА": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/5MidSCgff2oV8w6avZHvvxEiiBTaqF.png",
    "Сергеенко МА": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/bxKmqw0aCmfVewCpDrNC1PIPclznmUEdRTRD4kfk.jpg",
    "Николаева АС": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/5ttqdftNEQlyKNpy6eN9x6kRDUllgK.jpg",
    "Малышева КВ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/xMbxCMRVHabG7tRAaLo1qLpMeEfTeR.jpg",
    "Суренкова ДА": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/FXqNVjJEkhKG5Fia2eqQw5O4qQFMRk.jpg",
    "Лебедева АФ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/EyfQbwvks9uZ87i6AzcOd1JutmxMtJ.png",
    "Биешева АВ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/F2DfWqKWcJfORJx4yK35ug17ZISmkbXXgISEGUTk.jpg",
    "Миронова АА": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/JlZEv4xEZnFnqN8yA5yf1yZEcTBQSE.png",
    "Федорченко АВ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/8x3hivtefqG45Cson4cYt16lruYyWM.png",
    "Голышева МФ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/GpXpsY60kviDja1MXJPTTsWFWlwk0L.jpg",
    "Кислица НВ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/G3HfQ0lpD4VCrge9DfZGtr10VByytY.png",
    "Савченкова ЮВ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/E8pF7KjRK6kp09lo49BFcejQEP2uuv.png",
    "Малых ИБ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/LBN9MnFU77tEoDtDXPVIj7mBaQD6ud.png",
    "Ершова ИС": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/KlLl4CavaRurXMPF18MNDOal9li09A.png",
    "Аладина ГС": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/WJTH5FddNTucLk4QR9tWt4CWJn5u1lVKRCwF7qd8.png",
    "Неверова ЕВ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/c7BVOuQmyMbWjAV7jZTANlYJG7jeFdvfOBfR1gCg.png",
    "Яковлева ЛИ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/1sRXjuBl9HuUWw45w3Q4oxO5IlHM1u.png",
    "Панкратова ЕИ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/2i8XpxrwEXxXZylq0dlCHCTbuNaIxB.png",
    "Чуйкова МН": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/x51j3YumWIvW3bH4rwZuqTgtpI0K8j.png",
    "Саранчина ЕВ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/a6SmsYnD15J7CtUaHV7bk3tcNjMdg3.png",
    "Сидельникова ЛР": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/17l04ETLqi5n3Nt3GeGkxMBpMxrYPo.png",
    "Лунеко АИ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/yTJgNF77IfWnlVgCFyhPjOvklUB3SM.png",
    "Рыбальченко ЕВ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/N5Nqj3XOuj7kv6gzs3B8xHmaZZgNV6.png",
    "Полякова АС": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/Zn46wqnfFhGtmViAYhbkOjCmb4GH0i.png",
    "Авраменко ВВ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/ReLprnstM3479V7dqd10LPaTvd8Rs9.png",
    "Капитонова ЛП": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/nLmV6IKz9GzFCmioAAUPgwCXKeVERL.png",
    "Ханнанова ФР": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/dgHWGq3ugEl54V3sOphpkWVesowdY1.png",
    "Васильева ИИ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/DdbDhX1x4sjPFtvW5OkQ5Nkr7dxO6Y.png",
    "Григорьева-Домашняя ДД": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/2cjIZHXRUAFhF6jKlHVFGtC6srx2kg.png",
    "Стельмахова ДА": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/siOW5Sn9Hjz1xjcn5OHSfhIS5Am7lZkwknfVaUvP.jpg",
    "Галанцева АВ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/YHviv8B1L1sezhL2Zq2RS8my5Z3vr8.png",
    "Покусаева МА": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/IJhEMAKbGICbePC1Zogli4WsAH2Epm.png",
    "Идрисова ВА": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/J95c7rur1Qys00IpHzgVCivn9MEKer.png",
    "Давыдова МА": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/1nuIqNzMAvhm4o8ckbBSKiJ0RMAe9W.jpg",
    "Курешова АВ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/k8tdZVT2gPhTJpdOxR1dharFC7mHAb.png",
    "Корочанская АА": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/AImjGCQqJnyaBCki6djxiAgekdIxfs.png",
    "Баранова АА": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/fh9BmrZtv7IHClTVNmPzMnZLWtipGm.png",
    "Иванова НД": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/0pxvHUIWDsiidZDSRERsneGJkM5ryn.png",
    "Колосова ИИ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/Je9ndrGTGohPa522oQwzdzV23koQUx.png",
    "Осина АИ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/cIIqtMKAZYSdQoSoZPUaejYGJ3Ryd8.jpg",
    "Субботина ЮВ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/DKUGGRULIbsKhXNmI0d3TkZmf8wzQh.jpg",
    "Столетова НК": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/ANSGmPYl4XEE7tF8Xm07PovXZxH5yq.png",
    "Панферова КА": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/nZX9X8JWhSKM6wjwAUVoNpE2QN8jzm.jpg",
    "Карпова МЮ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/Lf1eQ89qfal1FJgoYPqlRXKsILAkSXbVSUTLvvyR.jpg",
    "Гусельникова АС": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/KgPWG71oVWyMsAXeLoAaVI5sExOkO7.png",
    "Ломоносова СА": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/EjL5lW5g3nMMzvyooIjwHLnjHFjzQzEB6WqwSKM0.jpg",
    "Макаровская ЕА": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/MD4FK3l0QmngUfyiZTwTXLiWw2Ikgyx6qTk7lPiv.png",
    "Пегушина НВ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/d4MamtbizC0OMBLDBeSifP3TcQTHvg.jpg",
    "Стороженко АВ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/dlXygcDCmvRzOO3GxnFFBLVXbeurEe6GmWxMVQRv.png",
    "Манахова ОС": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/BoIz908TC2a89gwt2IhhuJ2OrYUo2W.png",
    "Твердовская АВ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/fTJVNJFm6JiOXtfI8vRVAseWxFdhGI.jpg",
    "Кладко ЕС": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/VUhsWouldqW2oQS3FWCtsk9EnVU4ya.png",
    "Гринева АН": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/cVJghjSZP8uGlsEwQ7mw3J4LNZmB2Q.png",
    "Скотникова ДС": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/ogFGOunRMYhAt9knTLnpHAhiBU6rlN.png",
    "Горюнова АА": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/7nDaWJw9YMH6xkRpnDXpzGjR1BidBg.png",
    "Гласс ЕИ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/aqnYfu0SSRRMoOCPlDjBiheWstDhZb.png",
    "Черкашина АЕ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/AqyJu00yf0rCAqNjx0SXGfHwuVnxVg.jpg",
    "Приблуда АВ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/t1X3kjI7yHm9GbcsGAAKtsGNvo1FnJ.jpg",
    "Савельева ЕА": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/ifl3lIRVbjwPLL6TwrjeeXfUBhjgCs.png",
    "Краузе КА": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/rJLxtB8o80bmfq1uk7FSshqVAfQoOG.png",
    "Щеглова АВ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/7a1E5fe6wmMlbCFcD8tw16TzCpeAAn.jpg",
    "Белоусов ЮА": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/3AHw0ZOAMFreEtEQ1ua0OGEIRZWdVS.jpg",
    "Белогородская АЕ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/MPJr4hVDZJCCb44jX9f775R0BRmLSY.png",
    "Першина НА": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/ZMnNoe5M3IeI7bWT6XtaYCwzky2FpC.png",
    "Данилова ПС": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/sgxWY7c61GRRXmz49if7KmRYVTRIHcAfxUUXUP3f.jpg",
    "Лазуто ЯВ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/fkX6KB9C10jk0etNbXMA2VOlTSvLxM.png",
    "Бойко ТВ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/OUFBX027PJL6iRYIUubNkB6WqDZufO.jpg",
    "Фещенко ЕМ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/G7ZfEBrhaOgj2PZPBOQybLVaidNdjJ.png",
    "Надбитова АА": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/9ASCPUumoPxz9qlBiGywP865NJpbhq.png",
    "Крухмалева АВ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/gfVVgf8Ybi13eDnMxnDOzjf2Os8m4D.png",
    "Заметалина ИВ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/awlip233LmeEGFAbbFveNOYko03vrg.png",
    "Юдичева ПБ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/x2B6uw81GmG0bIgQNl7AVC3AdgJuFf.png",
    "Кисленкова АЮ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/UWk2Frq7MHXzS05kuc2N4vTBwNbLqQ.png",
    "Макаренко АГ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/iaBGPlmoYc5iciTtNJjD9eTBNa0f2Y.png",
    "Мозалевская ЕН": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/vgi0gDWneRvcUxb2LgVT2BPuOrBH0h.png",
    "Крушкова ЕМ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/6VMeS0uKu02nKlDqKQzpWYfRGeSDejsDrG1GFS3Y.jpg",
    "Шуда СВ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/bQipxNbnv1gGXfbEd3NN5wHe5Foi4w.png",
    "Багдасарьян ОВ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/LtmF1VRYEuBjM3nz1U0vP1CzWj7uaH.png",
    "Макаренко ОА": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/w4Mzgpr4aVFINMyb0zUDOavPZp6eVO.png",
    "Давыдова АВ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/9jieS7bKiOq6avJsSwrgPBCecq8XTT.png",
    "Анаевский КЕ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/mfr0a8YwtfkBwOgIsCvUWfCwhoaUnV.png",
    "Кулешова АВ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/x2bm7hrLiz3C9CoLSCYDCdi5WbH4mBokqnaYsvg0.png",
    "Пырх ТВ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/sHOTH7k1Sa0QI5nkWzDDvGvIY6SFed.png",
    "Мокина АР": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/riKTOuDW4hlyCIu04ZupU9vITB2kAm.png",
    "Минова АВ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/ndqdmmJb6STiAXQMKigy6rMSTOUZT6.png",
    "Бабенко ВВ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/vlN414hu3FxBp0VX0SsEVeeOWMN6L5.png",
    "Спиридонова НН": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/9LNmLkH6ffseMaStg5FfFyNQd2qfok.png",
    "Грязина НГ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/lVv2bEtUHyCHmyGEfEkmWV3pSh2Q7r.png",
    "Бариева ДС": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/2UflAku2p92G6Wn1EziYoMSd2VFTc8.png",
    "Бочкарёва НВ": "https://tmd-static-public.obs.ru-moscow-1.hc.sbercloud.ru/avatars/vt28Kz8ikgzkV9xfNGPVoGsxVsG06e.png",
}

STATUS_LABELS = {
    "approve": "✅ Нравится",
    "edit":    "✏️ Нужны правки",
    "decline": "❌ Отказываюсь от размещения",
}

def get_db():
    url = os.environ["DATABASE_URL"]
    # parse postgresql://user:pass@host:port/dbname
    url = url.replace("postgresql://", "").replace("postgres://", "")
    user_pass, rest = url.split("@")
    user, password = user_pass.split(":")
    host_port, dbname = rest.split("/")
    if ":" in host_port:
        host, port = host_port.split(":")
        port = int(port)
    else:
        host, port = host_port, 5432
    return pg8000.native.Connection(user=user, password=password, host=host, port=port, database=dbname, ssl_context=True)

def init_db():
    conn = get_db()
    conn.run("""
        CREATE TABLE IF NOT EXISTS responses (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            status TEXT NOT NULL,
            label TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT NOW()
        )
    """)
    conn.close()

def save_response(name: str, status: str):
    conn = get_db()
    conn.run(
        "INSERT INTO responses (name, status, label) VALUES (:name, :status, :label)",
        name=name, status=status, label=STATUS_LABELS.get(status, status)
    )
    conn.close()

def already_responded(name: str) -> bool:
    conn = get_db()
    rows = conn.run("SELECT 1 FROM responses WHERE name = :name LIMIT 1", name=name)
    conn.close()
    return len(rows) > 0

BASE_STYLE = """
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link href="https://fonts.googleapis.com/css2?family=Unbounded:wght@400;600&family=Inter:wght@300;400;500&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  :root {
    --bg: #0f1117; --surface: #1a1d27; --border: #2a2d3a;
    --text: #e8eaf0; --muted: #6b7280; --accent: #4f8ef7;
  }
  body {
    background: var(--bg); color: var(--text);
    font-family: 'Inter', sans-serif; min-height: 100vh;
    display: flex; align-items: center; justify-content: center; padding: 24px;
  }
  .card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 16px; padding: 40px; width: 100%; max-width: 480px;
    animation: fadeUp .4s ease both;
  }
  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  .logo {
    font-family: 'Unbounded', sans-serif; font-size: 13px; font-weight: 600;
    letter-spacing: .08em; color: var(--accent); text-transform: uppercase; margin-bottom: 32px;
  }
  h1 { font-family: 'Unbounded', sans-serif; font-size: 20px; font-weight: 600; line-height: 1.3; margin-bottom: 8px; }
  p.sub { color: var(--muted); font-size: 14px; line-height: 1.6; margin-bottom: 28px; }
  label { display: block; font-size: 12px; font-weight: 500; color: var(--muted); text-transform: uppercase; letter-spacing: .06em; margin-bottom: 8px; }
  input[type="text"] {
    width: 100%; background: var(--bg); border: 1px solid var(--border);
    border-radius: 10px; color: var(--text); font-family: 'Inter', sans-serif;
    font-size: 16px; padding: 14px 16px; outline: none; transition: border-color .2s;
  }
  input[type="text"]:focus { border-color: var(--accent); }
  .btn-primary {
    display: block; width: 100%; margin-top: 16px; padding: 14px;
    background: var(--accent); color: #fff; font-family: 'Inter', sans-serif;
    font-size: 15px; font-weight: 500; border: none; border-radius: 10px;
    cursor: pointer; transition: opacity .2s;
  }
  .btn-primary:hover { opacity: .88; }
  .photo-wrap {
    border-radius: 12px; overflow: hidden; margin-bottom: 28px;
    border: 1px solid var(--border); background: var(--bg);
    aspect-ratio: 3/4; display: flex; align-items: center; justify-content: center;
  }
  .photo-wrap img { width: 100%; height: 100%; object-fit: cover; display: block; }
  .actions { display: flex; flex-direction: column; gap: 10px; }
  .btn-action {
    display: flex; align-items: center; gap: 12px; padding: 14px 18px;
    border-radius: 10px; border: 1px solid var(--border); background: var(--bg);
    color: var(--text); font-family: 'Inter', sans-serif; font-size: 15px;
    cursor: pointer; transition: border-color .2s, background .2s; text-align: left;
  }
  .btn-action:hover { border-color: var(--accent); background: rgba(79,142,247,.07); }
  .btn-action .icon { font-size: 18px; flex-shrink: 0; }
  .error {
    background: rgba(239,68,68,.1); border: 1px solid rgba(239,68,68,.3);
    border-radius: 10px; padding: 12px 16px; font-size: 14px; color: #fca5a5; margin-top: 14px;
  }
  .hint { font-size: 12px; color: var(--muted); margin-top: 8px; }
  .doctor-name { font-size: 12px; color: var(--muted); margin-bottom: 20px; }
  .doctor-name span { color: var(--accent); font-weight: 500; }
</style>
"""

ENTER_HTML = """<!DOCTYPE html><html><head>""" + BASE_STYLE + """<title>Медблок</title></head><body>
<div class="card">
  <div class="logo">Медблок</div>
  <h1>Согласование фотографии</h1>
  <p class="sub">Введите вашу фамилию и инициалы, чтобы увидеть фото для размещения.</p>
  <form method="POST" action="/photo">
    <label for="name">Фамилия и инициалы</label>
    <input type="text" id="name" name="name" placeholder="Например: Иванова НД" autocomplete="off" autofocus>
    <div class="hint">Формат: Фамилия ИО (без точек)</div>
    {% if error %}<div class="error">{{ error }}</div>{% endif %}
    <button type="submit" class="btn-primary">Продолжить →</button>
  </form>
</div></body></html>"""

PHOTO_HTML = """<!DOCTYPE html><html><head>""" + BASE_STYLE + """<title>Медблок</title></head><body>
<div class="card">
  <div class="logo">Медблок</div>
  <h1>Ваше фото</h1>
  <p class="sub">Рассмотрите фотографию и выберите решение.</p>
  <div class="doctor-name"><span>{{ name }}</span></div>
  <div class="photo-wrap">
    <img src="{{ image_url }}" alt="Ваше фото" onerror="this.style.display='none'">
  </div>
  <form method="POST" action="/respond">
    <input type="hidden" name="name" value="{{ name }}">
    <div class="actions">
      <button type="submit" name="status" value="approve" class="btn-action"><span class="icon">✅</span> Да, нравится — можно размещать</button>
      <button type="submit" name="status" value="edit" class="btn-action"><span class="icon">✏️</span> Нужны правки</button>
      <button type="submit" name="status" value="decline" class="btn-action"><span class="icon">❌</span> Отказываюсь от размещения</button>
    </div>
  </form>
</div></body></html>"""

DONE_HTML = """<!DOCTYPE html><html><head>""" + BASE_STYLE + """<title>Медблок</title></head><body>
<div class="card" style="text-align:center;">
  <div class="logo">Медблок</div>
  <div style="font-size:48px;margin-bottom:20px;">{{ icon }}</div>
  <h1>{{ title }}</h1>
  <p class="sub" style="margin-top:10px;">{{ message }}</p>
</div></body></html>"""

ALREADY_HTML = """<!DOCTYPE html><html><head>""" + BASE_STYLE + """<title>Медблок</title></head><body>
<div class="card" style="text-align:center;">
  <div class="logo">Медблок</div>
  <div style="font-size:48px;margin-bottom:20px;">🔒</div>
  <h1>Ответ уже принят</h1>
  <p class="sub" style="margin-top:10px;">Вы уже отправили решение. Если нужно изменить — свяжитесь с администратором.</p>
</div></body></html>"""

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
    image_url = DOCTORS[name]
    return render_template_string(PHOTO_HTML, name=name, image_url=image_url)

@app.route("/respond", methods=["POST"])
def respond():
    name = request.form.get("name", "").strip()
    status = request.form.get("status", "").strip()
    if not name or name not in DOCTORS or status not in STATUS_LABELS:
        return redirect(url_for("index"))
    if already_responded(name):
        return render_template_string(ALREADY_HTML)
    save_response(name, status)
    messages = {
        "approve": ("✅", "Спасибо!", "Ваше согласие зафиксировано. Фото будет размещено."),
        "edit":    ("✏️", "Принято!", "Мы получили запрос на правки. Скоро свяжемся с вами."),
        "decline": ("❌", "Принято!", "Отказ зафиксирован. Фото размещено не будет."),
    }
    icon, title, message = messages[status]
    return render_template_string(DONE_HTML, icon=icon, title=title, message=message)

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
