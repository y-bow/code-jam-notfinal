from app import create_app
from app.models import (
    db, User, Student, Teacher, School, Section,
    Course, Enrollment, TimetableEntry, bcrypt,
    ProfessorAssistant
)
from datetime import datetime

app = create_app()

# =====================================================================
# DATA CONSTANTS
# =====================================================================

SECTION_1_STUDENTS = [
    {"name": "Lakkavaram Sripada Gayathri", "email": "sripadagayathri.l-29@scds.saiuniversity.edu.in"},
    {"name": "Ram Mouli", "email": "ram.m1-29@scds.saiuniversity.edu.in"},
    {"name": "Raghav Sudhakaran", "email": "raghav.s-29@scds.saiuniversity.edu.in"},
    {"name": "Jessika S", "email": "jessika.s-29@scds.saiuniversity.edu.in"},
    {"name": "Baladithya T", "email": "balaaditya.t-29@scds.saiuniversity.edu.in"},
    {"name": "Shilpa Sharma", "email": "shilpasharma.s-29@scds.saiuniversity.edu.in"},
    {"name": "Niharika D", "email": "niharika.d-29@scds.saiuniversity.edu.in"},
    {"name": "Santhosh Srinivasan", "email": "santhosh.s-29@scds.saiuniversity.edu.in"},
    {"name": "M Meera", "email": "meera.m-29@scds.saiuniversity.edu.in"},
    {"name": "R Sai Sanjay", "email": "saisanjay.r-29@scds.saiuniversity.edu.in"},
    {"name": "Dhanvanth Ravichandran", "email": "dhanvanth.r-29@scds.saiuniversity.edu.in"},
    {"name": "Sahana Mukundan", "email": "sahana.m-29@scds.saiuniversity.edu.in"},
    {"name": "Aitha Sree Sai Tanay", "email": "sreeasaitany.a-29@scds.saiuniversity.edu.in"},
    {"name": "Vaka Gayasree Reddy", "email": "gayasreereddy.v-29@scds.saiuniversity.edu.in"},
    {"name": "Sriguhan C S", "email": "sriguhan.c-29@scds.saiuniversity.edu.in"},
    {"name": "Shaik Mujimel", "email": "mujimel.s-29@scds.saiuniversity.edu.in"},
    {"name": "Cherukuri Hima Kethan", "email": "himakethan.c-29@scds.saiuniversity.edu.in"},
    {"name": "Vanka Vyoma Sai", "email": "vyomasai.v-29@scds.saiuniversity.edu.in"},
    {"name": "P Krishna Kishore", "email": "krishnakishore.p1-29@scds.saiuniversity.edu.in"},
    {"name": "Avula Disu Sandhya", "email": "sandhya.a-29@scds.saiuniversity.edu.in"},
    {"name": "A Uday Tej Reddy", "email": "uday.a-29@scds.saiuniversity.edu.in"},
    {"name": "Kavanoor Jeevana", "email": "jeevana.k-29@scds.saiuniversity.edu.in"},
    {"name": "Ane Rishendra", "email": "rishendra.a-29@scds.saiuniversity.edu.in"},
    {"name": "Hemasree R", "email": "hemasree.r-29@scds.saiuniversity.edu.in"},
    {"name": "Mahavadi Mohith Sarma", "email": "mohithsarma.m-29@scds.saiuniversity.edu.in"},
    {"name": "Ramachandruni V S Krishna Karthik", "email": "krishnakarthik.r-29@scds.saiuniversity.edu.in"},
    {"name": "Malladi Karthika", "email": "karthika.m-29@scds.saiuniversity.edu.in"},
    {"name": "Rokkam Shailesh Karthick", "email": "shaileshkarthick.r-29@scds.saiuniversity.edu.in"},
    {"name": "Kasya Lasya Gama Priya", "email": "lasyagamapriya.k-29@scds.saiuniversity.edu.in"},
    {"name": "Iska Lokesh Kumar", "email": "lokeshkumar.i-29@scds.saiuniversity.edu.in"},
    {"name": "Laki Reddy Varshini", "email": "varshini.l-29@scds.saiuniversity.edu.in"},
    {"name": "Kova Navitha Sai Sree", "email": "navithasaisree.k-29@scds.saiuniversity.edu.in"},
    {"name": "Ruthikka Arunkumar", "email": "ruthikka.a-29@scds.saiuniversity.edu.in"},
    {"name": "Kolluri Navya Vijaya Sree", "email": "navyavijayasree.k-29@scds.saiuniversity.edu.in"},
    {"name": "Palavali Midhun Reddy", "email": "midhunreddy.p-29@scds.saiuniversity.edu.in"},
    {"name": "Thummala Chetan Kumar", "email": "chetankumar.t-29@scds.saiuniversity.edu.in"},
    {"name": "Gopisetty Bhagya Varshini", "email": "bhagyavarshini.g-29@scds.saiuniversity.edu.in"},
    {"name": "Astakala Saketh", "email": "saketh.a-29@scds.saiuniversity.edu.in"},
    {"name": "Mulla Muhammed Maheboob", "email": "mullamuhammed.m-29@scds.saiuniversity.edu.in"},
    {"name": "Jarugula Amulya", "email": "amulya.j-29@scds.saiuniversity.edu.in"},
    {"name": "Gogireddy Vishnu Vardhan Reddy", "email": "vishnuvardhan.g-29@scds.saiuniversity.edu.in"},
    {"name": "Atmakuru Venkat Charan", "email": "venkatcharan.a-29@scds.saiuniversity.edu.in"},
    {"name": "D Advika", "email": "advika.d-29@scds.saiuniversity.edu.in"},
    {"name": "Shaik Mohammed Aymen", "email": "mohammedaymen.s-29@scds.saiuniversity.edu.in"},
    {"name": "Chembeti Guru Sai Charan", "email": "saicharan.c-29@scds.saiuniversity.edu.in"},
    {"name": "Narisetty Nithish Kumar", "email": "nithishkumar.n-29@scds.saiuniversity.edu.in"},
    {"name": "Buyyareddy Deepthi", "email": "deepthi.b-29@scds.saiuniversity.edu.in"},
    {"name": "Chembeti Tejesh", "email": "tejesh.c-29@scds.saiuniversity.edu.in"},
    {"name": "Aravabhumi Dharma Teja", "email": "dharmateja.a-29@scds.saiuniversity.edu.in"},
    {"name": "Salava Santhosh Kumar", "email": "santhoshkumar.s-29@scds.saiuniversity.edu.in"},
    {"name": "Subhan Sarangi", "email": "subhan.s-29@scds.saiuniversity.edu.in"},
    {"name": "Paladugu balaji", "email": "balaji.p-29@scds.saiuniversity.edu.in"},
    {"name": "Vemula Jayakrishna", "email": "jayakrishna.v-29@scds.saiuniversity.edu.in"},
    {"name": "Rayi Nishitha", "email": "nishitha.r-29@scds.saiuniversity.edu.in"},
    {"name": "Gurram Lokeswari", "email": "lokeswari.g-29@scds.saiuniversity.edu.in"},
    {"name": "P Sudeep", "email": "sudeep.p-29@scds.saiuniversity.edu.in"},
    {"name": "Madala Tejaswi", "email": "tejaswi.m-29@scds.saiuniversity.edu.in"},
    {"name": "Vemala Sailesh", "email": "sailesh.v-29@scds.saiuniversity.edu.in"},
    {"name": "Mallavarapu Sai Charan Kumar Reddy", "email": "saicharan.m1-29@scds.saiuniversity.edu.in"},
    {"name": "Medikonda Adithya Vardhan", "email": "adithyavardhan.m-29@scds.saiuniversity.edu.in"},
    {"name": "Nagaraju danaboena", "email": "nagaraju.d-29@scds.saiuniversity.edu.in"},
    {"name": "Shaik Shareef", "email": "shareef.s-29@scds.saiuniversity.edu.in"},
    {"name": "Pethuri N V L N Devamithra", "email": "devamithra.p-29@scds.saiuniversity.edu.in"},
    {"name": "Thiruvaipati Jahnavi", "email": "jahnavi.t-29@scds.saiuniversity.edu.in"},
    {"name": "Suru Yaswanth Reddy", "email": "yaswanthreddy.s-29@scds.saiuniversity.edu.in"},
    {"name": "Guduguntla Sahithi", "email": "sahithi.g-29@scds.saiuniversity.edu.in"},
    {"name": "Shaik Abdul Samad", "email": "abdulsamad.s-29@scds.saiuniversity.edu.in"},
    {"name": "Marripakula Teja", "email": "teja.m-29@scds.saiuniversity.edu.in"},
    {"name": "Buragadda Prasanth Sri", "email": "prasanthsri.b-29@scds.saiuniversity.edu.in"},
    {"name": "Rolla Manjula", "email": "manjula.r-29@scds.saiuniversity.edu.in"},
    {"name": "Devireddy Maheswari", "email": "maheswari.d-29@scds.saiuniversity.edu.in"},
    {"name": "Paturu Jeevan Krishna Kishore", "email": "krishnakishore.p-29@scds.saiuniversity.edu.in"},
    {"name": "Peram Tejas", "email": "tejas.p-29@scds.saiuniversity.edu.in"},
    {"name": "Gubala venkata sree teja", "email": "venkatasreeteja.g-29@scds.saiuniversity.edu.in"},
    {"name": "Shaik Safivulla", "email": "safivulla.s-29@scds.saiuniversity.edu.in"},
    {"name": "Anamalagundam Greeshma", "email": "greeshma.a-29@scds.saiuniversity.edu.in"},
    {"name": "Anamalagundam Jaswanth", "email": "jaswanth.a-29@scds.saiuniversity.edu.in"},
    {"name": "Nafeesa Zainul", "email": "zainul.n-29@scds.saiuniversity.edu.in"},
    {"name": "Bellamkonda Greeshma", "email": "greeshma.b-29@scds.saiuniversity.edu.in"},
    {"name": "Pathangi Mokshagna Rao", "email": "mokshagna.p-29@scds.saiuniversity.edu.in"},
    {"name": "Burra Sreenivas", "email": "sreenivas.b-29@scds.saiuniversity.edu.in"},
    {"name": "Morilla Reddy Mahesh Reddy", "email": "maheshreddy.m-29@scds.saiuniversity.edu.in"},
    {"name": "Kottam Sravan Gowtham", "email": "sravangowtham.k-29@scds.saiuniversity.edu.in"},
    {"name": "Savuturi Samuel Daniel", "email": "samueldaniel.s-29@scds.saiuniversity.edu.in"},
    {"name": "Kilari Thanu Sree", "email": "thanusree.k-29@scds.saiuniversity.edu.in"},
    {"name": "Amruta Kandaswamy", "email": "amruta.k-29@scds.saiuniversity.edu.in"}
]

SECTION_2_STUDENTS = [
    ("Moravineni Jishnu Teja", "jishnuteja.m-29@scds.saiuniversity.edu.in"),
    ("Oreddy Sai Praharsa Reddy", "praharsareddy.o-29@scds.saiuniversity.edu.in"),
    ("Kadiveti Nivas", "nivas.k-29@scds.saiuniversity.edu.in"),
    ("Rachuri Harsha Vardhan", "harshavardhan.r-29@scds.saiuniversity.edu.in"),
    ("Polisetty Venkata Surya Jathin", "venkatasuryajathin.p-29@scds.saiuniversity.edu.in"),
    ("Seepareddy Amarnath Reddy", "amarnathreddy.s-29@scds.saiuniversity.edu.in"),
    ("Dirisala Sai Venkata Kartheek", "saivenkatakartheek.d-29@scds.saiuniversity.edu.in"),
    ("Shaik Sadhik", "sadhik.s-29@scds.saiuniversity.edu.in"),
    ("Sakam Mokshitha Reddy", "mokshithareddy.s-29@scds.saiuniversity.edu.in"),
    ("Gampanapalli Karthik", "karthik.g-29@scds.saiuniversity.edu.in"),
    ("Gadipudi Pranathi", "pranathi.g-29@scds.saiuniversity.edu.in"),
    ("Cheppali Ummar Farook", "ummarfarook.c-29@scds.saiuniversity.edu.in"),
    ("Pudota Akhil", "akhil.p-29@scds.saiuniversity.edu.in"),
    ("Vulli Geeta", "geetha.v-29@scds.saiuniversity.edu.in"),
    ("Chaganti Avinash", "avinash.c-29@scds.saiuniversity.edu.in"),
    ("Dasam Sai Sadhvik", "saisadhvik.d-29@scds.saiuniversity.edu.in"),
    ("Dandu Mohith Varma", "mohithvarma.d-29@scds.saiuniversity.edu.in"),
    ("Marrikanti Venkata Dhanush", "venkatadhanush.m-29@scds.saiuniversity.edu.in"),
    ("Angina Pradeep Kumar", "pradeepkumar.a-29@scds.saiuniversity.edu.in"),
    ("Velpula Sai Sravan", "saisravan.v-29@scds.saiuniversity.edu.in"),
    ("Marrigunta Sai Charan", "saicharan.m-29@scds.saiuniversity.edu.in"),
    ("Boddu Mani Sampreeth Reddy", "manisampreeth.b-29@scds.saiuniversity.edu.in"),
    ("Maniswar Reddy Boddu", "maniswarreddy.b-29@scds.saiuniversity.edu.in"),
    ("Bodi Hari Babu", "bodihari.b-29@scds.saiuniversity.edu.in"),
    ("Chandra Padmaja", "padmaja.c-29@scds.saiuniversity.edu.in"),
    ("Shaik Khaja Nawaz", "khajanawaz.s-29@scds.saiuniversity.edu.in"),
    ("Shaik Rushma", "rushma.s-29@scds.saiuniversity.edu.in"),
    ("Gangavarapu Pradeep", "pradeep.g-29@scds.saiuniversity.edu.in"),
    ("Rithul S", "rithul.s-29@scds.saiuniversity.edu.in"),
    ("Rudraraju Srikar Siva Phani Padmaraju", "srikarsivaphanipadmaraju.r-29@scds.saiuniversity.edu.in"),
    ("Besta Manasa Udayini", "manasaudayini.b-29@scds.saiuniversity.edu.in"),
    ("Yarramasetti Sai Eswar", "saieswar.y-29@scds.saiuniversity.edu.in"),
    ("Bommanahal Jaswanth Chowdary", "jaswanth.b-29@scds.saiuniversity.edu.in"),
    ("Madala Gopi Chandu", "gopichandu.m-29@scds.saiuniversity.edu.in"),
    ("Vajrala Spandana", "spandana.v-29@scds.saiuniversity.edu.in"),
    ("Pemmasani Dheeraj", "dheeraj.p-29@scds.saiuniversity.edu.in"),
    ("Gundala Venkata Himesh", "venkathimesh.g-29@scds.saiuniversity.edu.in"),
    ("Pemmasani Eswaradesh", "eswardesh.p-29@scds.saiuniversity.edu.in"),
    ("Kommi Harshith", "harshith.k-29@scds.saiuniversity.edu.in"),
    ("Tumu Indra Reddy", "indrareddy.t-29@scds.saiuniversity.edu.in"),
    ("Maddela Nanda Kishore", "nandakishore.m-29@scds.saiuniversity.edu.in"),
    ("Bommaka Harshitha", "harshitha.b-29@scds.saiuniversity.edu.in"),
    ("Pagadala Venkata Prabhu Likith", "prabhulikith.p-29@scds.saiuniversity.edu.in"),
    ("Bombothula Mohan Vamsi Yadav", "mohanvamsiyadav.b-29@scds.saiuniversity.edu.in"),
    ("Turupusima Chavva Harshitha Reddy", "harshithareddy.t-29@scds.saiuniversity.edu.in"),
    ("Sandrapalli Jahnavi", "jahnavi.s-29@scds.saiuniversity.edu.in"),
    ("Banu Prakash Ramapuram", "prakash.b-29@scds.saiuniversity.edu.in"),
    ("Garikipati Akshaya", "akshaya.g-29@scds.saiuniversity.edu.in"),
    ("Chaganti Chennakesava Srikar Reddy", "srikarreddy.c-29@scds.saiuniversity.edu.in"),
    ("Thota Thrishika", "thrishika.t-29@scds.saiuniversity.edu.in"),
    ("Chemudugunta Thanush", "thanush.c-29@scds.saiuniversity.edu.in"),
    ("Balasamudram Sai Charan", "saicharan.b-29@scds.saiuniversity.edu.in"),
    ("Oggu Madhu Priya", "madhupriya.o-29@scds.saiuniversity.edu.in"),
    ("Baddam Ranjith Reddy", "ranjithreddy.b-29@scds.saiuniversity.edu.in"),
    ("Dudekula Thanveer", "thanveer.d-29@scds.saiuniversity.edu.in"),
    ("Dhanyasi Sandesh Joyal", "sandeshjoyal.d-29@scds.saiuniversity.edu.in"),
    ("Maramreddy Sulakshan Reddy", "sulakshanreddy.m-29@scds.saiuniversity.edu.in"),
    ("Singari Dinesh", "dinesh.s-29@scds.saiuniversity.edu.in"),
    ("Yeduru Lavanya", "lavanya.y-29@scds.saiuniversity.edu.in"),
    ("Gutti Jitendra Pavan", "jitendrapavan.g-29@scds.saiuniversity.edu.in"),
    ("Budhala Pardeep", "pardeep.b-29@scds.saiuniversity.edu.in"),
    ("Yeturi Rakesh", "rakesh.y-29@scds.saiuniversity.edu.in"),
    ("Zaahin Bhattacharyya", "zaahin.b-29@scds.saiuniversity.edu.in"),
    ("Pera Charan Kumar Reddy", "charankumarreddy.p-29@scds.saiuniversity.edu.in"),
    ("Padarthi Mohan Shabariash", "mohansabarish.p-29@scds.saiuniversity.edu.in"),
    ("Pikkili Dharma Sai Kumar", "dharmasaikumar.p-29@scds.saiuniversity.edu.in"),
    ("Pasupuleti Mognesh", "mognesh.p-29@scds.saiuniversity.edu.in"),
    ("Chenna Reddy Gari Manoj Reddy", "garimanojreddy.c-29@scds.saiuniversity.edu.in"),
    ("Unnam Manmohan", "manmohan.u-29@scds.saiuniversity.edu.in"),
    ("Edamalakandi Chaturved", "chaturved.e-29@scds.saiuniversity.edu.in"),
    ("Eswar Sangeetha", "sangeetha.e-29@scds.saiuniversity.edu.in"),
    ("Pagadala Riddhima", "ruddhima.p-29@scds.saiuniversity.edu.in"),
    ("Singamala Santhosh Reddy", "santhoshreddy.s-29@scds.saiuniversity.edu.in"),
    ("Koncha Venkata Ravi Teja Reddy", "ravitejareddy.k-29@scds.saiuniversity.edu.in"),
    ("Koncha Pradeep", "pradeep.k-29@scds.saiuniversity.edu.in"),
    ("Iska Sri Charan", "sricharan.i-29@scds.saiuniversity.edu.in"),
    ("Sai Manikanta Vinay Malireddy", "manikantavinay.s-29@scds.saiuniversity.edu.in"),
    ("Jana Phani Kumar", "phanikumar.j-29@scds.saiuniversity.edu.in"),
    ("Gangisetti Vikas Sri Raj", "vikassriraj.g-29@scds.saiuniversity.edu.in"),
    ("Gangisetti Hemanth Sai Krishna", "hemanthsai.g-29@scds.saiuniversity.edu.in"),
    ("Maddirla Manoj Kumar Reddy", "manojkumarreddy.m-29@scds.saiuniversity.edu.in"),
    ("Alahari Venkata Sai Santhosh", "saisanthosh.a-29@scds.saiuniversity.edu.in"),
    ("Mullagoori Arjun", "arjun.m-29@scds.saiuniversity.edu.in"),
    ("Lukkani Deepak", "deepak.l-29@scds.saiuniversity.edu.in"),
    ("Patnam Manas Tej", "manastej.p-29@scds.saiuniversity.edu.in")
]

SECTION_3_STUDENTS = [
    ("Gangapurapu Jai Charan",              "jaicharan.g-29@scds.saiuniversity.edu.in"),
    ("Payyavula Shashank",                   "shashank.p-29@scds.saiuniversity.edu.in"),
    ("Dondati Pradeep",                      "pradeep.d-29@scds.saiuniversity.edu.in"),
    ("G Yoshithaa Sree",                     "yoshithaasree.g-29@scds.saiuniversity.edu.in"),
    ("Konapalli Poojitha",                   "poojitha.k-29@scds.saiuniversity.edu.in"),
    ("Mandem Sai Vani",                      "saivani.m-29@scds.saiuniversity.edu.in"),
    ("Thirividhi Jaswanth",                  "jaswanth.t-29@scds.saiuniversity.edu.in"),
    ("Chennuru Veera Manjunatha Reddy",      "manjunathareddy.c-29@scds.saiuniversity.edu.in"),
    ("Kajjayam Sai Mourya",                  "saimourya.k-29@scds.saiuniversity.edu.in"),
    ("Mekala Navya Sri",                     "navyasri.m-29@scds.saiuniversity.edu.in"),
    ("Kattamreddy Lakshmi Chaitra",          "lakshmichaitra.k-29@scds.saiuniversity.edu.in"),
    ("Chanduluru Sanhitha Yadav",            "sanhithayadav.c-29@scds.saiuniversity.edu.in"),
    ("Malli Divya",                          "divya.m-29@scds.saiuniversity.edu.in"),
    ("Dondati Pavitra",                      "pavitra.d-29@scds.saiuniversity.edu.in"),
    ("Ramireddy Siva Likitha Reddy",         "sivalikitha.r-29@scds.saiuniversity.edu.in"),
    ("Udatha Sri Vennela",                   "srivennela.u-29@scds.saiuniversity.edu.in"),
    ("Vagathuri Bhargava",                   "bhargava.v-29@scds.saiuniversity.edu.in"),
    ("Valapalli Ram Teja",                   "ramteja.v-29@scds.saiuniversity.edu.in"),
    ("Kamireddy Yoshith Reddy",              "yoshithreddy.k-29@scds.saiuniversity.edu.in"),
    ("Peddireddy Sai Darshan Reddy",         "saidarshanreddy.p-29@scds.saiuniversity.edu.in"),
    ("Innamuri Venkata Sai Lohith",          "venkatasai.i-29@scds.saiuniversity.edu.in"),
    ("Myla Pavan",                           "pavan.m-29@scds.saiuniversity.edu.in"),
    ("Duvvuru Deepak Reddy",                 "deepakreddy.d-29@scds.saiuniversity.edu.in"),
    ("P Tharun",                             "tharun.p-29@scds.saiuniversity.edu.in"),
    ("Pramidhala Hemanth",                   "hemanth.p-29@scds.saiuniversity.edu.in"),
    ("Marri Bhanu Sri",                      "bhanusri.m-29@scds.saiuniversity.edu.in"),
    ("Yelluri Harshavardhan Reddy",          "harshavardhanreddy.y-29@scds.saiuniversity.edu.in"),
    ("Rachavelpula Puneeth Sai",             "puneethsai.r-29@scds.saiuniversity.edu.in"),
    ("Siginam Sai Sathwik",                  "saisathwik.s-29@scds.saiuniversity.edu.in"),
    ("Palacharla Vamsi Krishna",             "vamsikrishna.p-29@scds.saiuniversity.edu.in"),
    ("Amarthaluru Bhavesh",                  "bhavesh.a-29@scds.saiuniversity.edu.in"),
    ("Telaganeni Lohith Manish",             "lohithmanish.t-29@scds.saiuniversity.edu.in"),
    ("Bangarugari Prathyush",                "prathyush.b-29@scds.saiuniversity.edu.in"),
    ("Mahasamudhram Girish Reddy",           "girishreddy.m-29@scds.saiuniversity.edu.in"),
    ("Golla Siva Tharun",                    "sivatharun.g-29@scds.saiuniversity.edu.in"),
    ("Manupati Poorna Chandra",              "poornaachandra.m-29@scds.saiuniversity.edu.in"),
    ("Rathinakumar S",                       "rathinakumar.s-29@scds.saiuniversity.edu.in"),
    ("Godduvelagala Chennakesava",           "chennakesava.g-29@scds.saiuniversity.edu.in"),
    ("Advait D",                             "advait.d-29@scds.saiuniversity.edu.in"),
    ("Yelchuri Ganesh",                      "ganesh.y-29@scds.saiuniversity.edu.in"),
    ("Dondlapadu Ramya Sree",                "ramyasree.d-29@scds.saiuniversity.edu.in"),
    ("Panyam Venkata Gyana Deepak",          "gyanadeepak.p-29@scds.saiuniversity.edu.in"),
    ("Ilupuru Padmajahnavi",                 "padmajahnavi.i-29@scds.saiuniversity.edu.in"),
    ("Malchi Sneha Sruthi",                  "snehasruthi.m-29@scds.saiuniversity.edu.in"),
    ("Devarinti Suma Sri",                   "sumasri.d-29@scds.saiuniversity.edu.in"),
    ("Badhvel Hansika Srinidhi",             "hansikasrinidhi.b-29@scds.saiuniversity.edu.in"),
    ("Pichika V Vyshnavi",                   "vyshnavi.p-29@scds.saiuniversity.edu.in"),
    ("Kannikapuram Teja",                    "teja.k-29@scds.saiuniversity.edu.in"),
    ("Chinka Sumanth",                       "sumanth.c-29@scds.saiuniversity.edu.in"),
    ("Arkadu Mokshitha",                     "mokshitha.a-29@scds.saiuniversity.edu.in"),
    ("Gajji Bhargavi",                       "bhargavi.g-29@scds.saiuniversity.edu.in"),
    ("Chagam Riteeswar Reddy",               "riteeswar.c-29@scds.saiuniversity.edu.in"),
    ("Kotagasti Taheer",                     "thaheer.k-29@scds.saiuniversity.edu.in"),
    ("Peravali Puvan Venkata Pavan",         "venkatapavan.p-29@scds.saiuniversity.edu.in"),
    ("Bathula Hanuma Kotireddy",             "hanumakotireddy.b-29@scds.saiuniversity.edu.in"),
    ("Yenneti Gowtham Sri Sai Srinivasa Murthy", "gowthamsri.y-29@scds.saiuniversity.edu.in"),
    ("Ramireddy Bhavadeep Reddy",            "bhavadeepreddy.r-29@scds.saiuniversity.edu.in"),
    ("Palisetti Harsha Deepika",             "deepikaharsha.p-29@scds.saiuniversity.edu.in"),
    ("Purini Tejeswar",                      "tejeswar.p-29@scds.saiuniversity.edu.in"),
    ("Nagireddy Naveen",                     "naveen.n-29@scds.saiuniversity.edu.in"),
    ("Vunnam Kowshik",                       "kowshik.v-29@scds.saiuniversity.edu.in"),
    ("Palleboyina Vamsi Krishna",            "vamsikrishna.pl-29@scds.saiuniversity.edu.in"),
    ("Venna Bhuvaneshwar",                   "bhuvaneshwar.v-29@scds.saiuniversity.edu.in"),
    ("Kilari Hithesh",                       "kilari.h-29@scds.saiuniversity.edu.in"),
    ("Boddu Vamsidhar Reddy",                "vamsidharreddy.b-29@scds.saiuniversity.edu.in"),
    ("Anbuchelvan V",                        "anbuchelvan.v-29@scds.saiuniversity.edu.in"),
    ("B Vaibhav",                            "vaibhav.b-29@scds.saiuniversity.edu.in"),
    ("S T Suneethra",                        "suneethra.s-29@scds.saiuniversity.edu.in"),
    ("Kolamasanapalli Manjunath",            "manjunath.k-29@scds.saiuniversity.edu.in"),
    ("Dhanemkula Veera Bhargav",             "veerabhargav.d-29@scds.saiuniversity.edu.in"),
    ("Ontimitta Keerthana",                  "keerthana.o-29@scds.saiuniversity.edu.in"),
    ("Koneru Haneeth",                       "haneeth.k-29@scds.saiuniversity.edu.in"),
    ("Golla Shiva Santhosh Reddy",           "shivasanthoshreddy.g-29@scds.saiuniversity.edu.in"),
    ("Vudata Sri Madhavan",                  "srimadhavan.v-29@scds.saiuniversity.edu.in"),
    # Rows 75-85 are Lab Group 8
    ("Dudi Venkata Krishna Karthik",         "venkatakrishnakarthik.d-29@scds.saiuniversity.edu.in"),
    ("Thati Sushmanth Reddy",                "sushmanthreddy.t-29@scds.saiuniversity.edu.in"),
    ("Mallela Mohammad Aqib",                "mohammadaqib.m-29@scds.saiuniversity.edu.in"),
    ("M Arun Kumar",                         "arunkumar.m-29@scds.saiuniversity.edu.in"),
    ("Dasari Venkata Yeswanth",              "venkatayaswanth.d-29@scds.saiuniversity.edu.in"),
    ("Boddu Chiranjeevi",                    "chiranjeevi.b-29@scds.saiuniversity.edu.in"),
    ("Gurram Mahesh",                        "mahesh.g-29@scds.saiuniversity.edu.in"),
    ("Ganugapenta Naga Mahesh",              "nagamahesh.g-29@scds.saiuniversity.edu.in"),
    ("Beeram Naga Maheswar Reddy",           "maheswar.b-29@scds.saiuniversity.edu.in"),
    ("Ayindla Surya",                        "surya.a-29@scds.saiuniversity.edu.in"),
    ("Narbavee V",                           "narbavee.v-29@scds.saiuniversity.edu.in"),
]

SECTION_5_STUDENTS = [
    ("Vasili Praharsha", "praharsha.v-29@scds.saiuniversity.edu.in", 8),
    ("Syed Mansoor", "mansoor.s-29@scds.saiuniversity.edu.in", 8),
    ("Nellimarla mohan thanush karthikeya sai", "mohanthanush.n-29@scds.saiuniversity.edu.in", 8),
    ("Nandyala Lakshmi Vijayanand Reddy", "vijayanand.n-29@scds.saiuniversity.edu.in", 8),
    ("Lakkireddy Iswarya", "iswarya.l-29@scds.saiuniversity.edu.in", 8),
    ("Shaik Arsheen", "arsheen.s-29@scds.saiuniversity.edu.in", 8),
    ("Kuraku Sri Balaji", "sribalaji.k-29@scds.saiuniversity.edu.in", 8),
    ("Gandikota Shaavanth", "shaavanth.g-29@scds.saiuniversity.edu.in", 8),
    ("Yeluri Srikanth Reddy", "srikanth.r-29@scds.saiuniversity.edu.in", 8),
    ("Pandi Ravi Kumar", "ravikumar.p-29@scds.saiuniversity.edu.in", 8),
]

SECTION_4_STUDENTS = [
    # Batch 1
    ("Mohamed Nibras S", "mohamednibras.s-29@scds.saiuniversity.edu.in"),
    ("Pokala Sunvith Kumar Reddy", "sunvithkumar.p-29@scds.saiuniversity.edu.in"),
    ("Palleti Ram Siddartha Reddy", "siddarthareddy.p-29@scds.saiuniversity.edu.in"),
    ("Belum Vishal Reddy", "vishal.b-29@scds.saiuniversity.edu.in"),
    ("Ambu Navya Reddy", "navya.a-29@scds.saiuniversity.edu.in"),
    ("Basireddy Chandra Sekhar Reddy", "chandrasekhar.b-29@scds.saiuniversity.edu.in"),
    ("Kommuru Venkata Sailendra Kumar", "sailendrakumar.k-29@scds.saiuniversity.edu.in"),
    ("Sharan Pranav", "sharanpranav.a-29@scds.saiuniversity.edu.in"),
    ("Avula Uma Maheswara Reddy", "umamaheswara.a-29@scds.saiuniversity.edu.in"),
    ("Avula Manogna", "manogna.a-29@scds.saiuniversity.edu.in"),
    ("Thanda Hanuma Karthikeya", "hanumakarthikeya.t-29@scds.saiuniversity.edu.in"),
    ("Jasmitha N R V", "jasmitha.n-29@scds.saiuniversity.edu.in"),
    ("Pandeti Sai Srinivas Raju", "saisrinivasraju.p-29@scds.saiuniversity.edu.in"),
    ("Raghupathi Harsha Nandini", "harshadini.r-29@scds.saiuniversity.edu.in"),
    ("Kotha Shanmukha Venkata Sai", "shanmukhaverkatasai.k-29@scds.saiuniversity.edu.in"),
    ("Madduri Kapil Sravan Kumar", "sravankumar.m-29@scds.saiuniversity.edu.in"),
    ("Ishwarya J S", "ishwarya.j-29@scds.saiuniversity.edu.in"),
    ("Edukulla Sai Prashanth", "saiprashanth.e-29@scds.saiuniversity.edu.in"),
    ("Sottu Sivaharsha", "sivaharsha.s-29@scds.saiuniversity.edu.in"),
    ("Metta Sujith", "sujith.m-29@scds.saiuniversity.edu.in"),
    ("Muttina Sai Santhosh", "saisanthosh.m-29@scds.saiuniversity.edu.in"),
    ("Kurapati Nishanth Kumar Reddy", "nishanthkumar.k-29@scds.saiuniversity.edu.in"),
    ("Bommuveera Bhargav Kumar Reddy", "bhargavkumarreddy.b-29@scds.saiuniversity.edu.in"),
    ("Ravuru Yaswanth Reddy", "yaswanthreddy.r-29@scds.saiuniversity.edu.in"),
    ("Shaik Sameer", "sameer.s-29@scds.saiuniversity.edu.in"),
    ("Pati Venkata Virat Nani Siddhik", "viratnanisiddhik.p-29@scds.saiuniversity.edu.in"),
    ("Vasam Chandana", "chandana.v-29@scds.saiuniversity.edu.in"),
    ("Lakkakula Charan Teja", "charanteja.l-29@scds.saiuniversity.edu.in"),
    # Batch 2
    ("Sirimavilla Vijaya Lakshmi", "vijayalakshmi.s-29@scds.saiuniversity.edu.in"),
    ("Bonthala Venkata Lakshmi Hema Varshini", "lakshmihemavarshini.b-29@scds.saiuniversity.edu.in"),
    ("Kamepalli Harichandra Prasad", "harichandra.k-29@scds.saiuniversity.edu.in"),
    ("Guntur Gokula Sai Balaji Vinay Kumar", "vinaykumar.g-29@scds.saiuniversity.edu.in"),
    ("Vayila Tirumala", "tirumala.v-29@scds.saiuniversity.edu.in"),
    ("Nunna Spandana", "spandana.n-29@scds.saiuniversity.edu.in"),
    ("Nunna Venkata Santhosh", "venkatasanthosh.n-29@scds.saiuniversity.edu.in"),
    ("Pasuluru Kummara Adil Kumar", "kumaraadilkumar.p-29@scds.saiuniversity.edu.in"),
    ("Thummala Madhulika", "madhulika.t-29@scds.saiuniversity.edu.in"),
    ("Yanamala Venkata Jeswanth Reddy", "jeswanthreddy.y-29@scds.saiuniversity.edu.in"),
    ("Akkala Jasvanth Reddy", "jasvanthreddy.a-29@scds.saiuniversity.edu.in"),
    ("Khyathi Teja Kethari", "tejakethari.k-29@scds.saiuniversity.edu.in"),
    ("Peddiveeti Venkata Harish", "venkataharish.p-29@scds.saiuniversity.edu.in"),
    ("V Viveka Vardhini", "vivekavardhini.v-29@scds.saiuniversity.edu.in"),
    ("Chilakala Poorna Chandra Reddy", "poornachandra.c-29@scds.saiuniversity.edu.in"),
    ("Nagineni Geetha", "geetha.n-29@scds.saiuniversity.edu.in"),
    ("Nuka Bhanu Prakash Reddy", "bhanuprakashreddy.n-29@scds.saiuniversity.edu.in"),
    ("Mudireddy Uma Maheswar Reddy", "umamaheswar.m-29@scds.saiuniversity.edu.in"),
    ("Amari Rishitha Sri", "rishithasri.a-29@scds.saiuniversity.edu.in"),
    ("Burreddy Mourya Karthik Reddy", "mouryakarthikreddy.b-29@scds.saiuniversity.edu.in"),
    ("Yatagiri Ajay Kumar", "ajaykumar.y-29@scds.saiuniversity.edu.in"),
    ("V Sanjay Shekar", "sanjayshekar.v-29@scds.saiuniversity.edu.in"),
    ("Siddula Karthikeya Reddy", "karthikeyareddy.s-29@scds.saiuniversity.edu.in"),
    ("Pabbisetty Abhilesh Sai", "abhileshsai.p-29@scds.saiuniversity.edu.in"),
    ("Tellapati Jaswanth", "jaswanth.t1-29@scds.saiuniversity.edu.in"),
    ("Bathala Sumanth", "sumanth.b-29@scds.saiuniversity.edu.in"),
    ("Rendeddula Sivanjith Reddy", "sivanjith.r-29@scds.saiuniversity.edu.in"),
    ("Vanama Hansika Pranavi", "hansikapranavi.v-29@scds.saiuniversity.edu.in"),
    ("Shaik Mohammad Hafeez", "hafeez.s-29@scds.saiuniversity.edu.in"),
    # Batch 3
    ("Yadla Shashank Venkat Sai", "venkatasai.y-29@scds.saiuniversity.edu.in"),
    ("Vidudala Abhinay Kumar", "abhinaykumar.v-29@scds.saiuniversity.edu.in"),
    ("Mangali Jai Shubhakanth", "jaishubhakanth.m-29@scds.saiuniversity.edu.in"),
    ("Koduru Guru Vignesh", "guruvignesh.k-29@scds.saiuniversity.edu.in"),
    ("Kuntumalla Madan Kumar", "madankumar.k-29@scds.saiuniversity.edu.in"),
    ("Bollineni Avinash", "avinash.b-29@scds.saiuniversity.edu.in"),
    ("Avula Laasya", "laasya.a-29@scds.saiuniversity.edu.in"),
    ("Balireddygari Deekshitha", "deekshitha.b-29@scds.saiuniversity.edu.in"),
    ("Jogiparthi Venkata Audi Siva Rama Teja", "audisiva.j-29@scds.saiuniversity.edu.in"),
    ("Valluri Dhushyanth Kumar", "dhushyanthkumar.v-29@scds.saiuniversity.edu.in"),
    ("Bokkasam Naga Saranya", "saranya.b-29@scds.saiuniversity.edu.in"),
    ("Erisetty Jetin", "jetin.e-29@scds.saiuniversity.edu.in"),
    ("Jammala Venkata Sai Tagore", "saitagore.j-29@scds.saiuniversity.edu.in"),
    ("Nossam Ramya Sruthi", "ramyasruthi.n-29@scds.saiuniversity.edu.in"),
    ("Patan Imran Khan", "imrankhan.p-29@scds.saiuniversity.edu.in"),
    ("Punugunta Venkata Mokshith", "mokshith.p-29@scds.saiuniversity.edu.in"),
    ("Shaik Mahammad Sharif", "sharif.s-29@scds.saiuniversity.edu.in"),
    ("Somu Naga Sharanya", "nagasharanya.s-29@scds.saiuniversity.edu.in"),
    ("Padarthi Venkata Naga Sai Nikhil", "nagasainikhil.p-29@scds.saiuniversity.edu.in"),
    ("Shaik Khadar Ujwal Thoufidh", "ujwalthoufidh.s-29@scds.saiuniversity.edu.in"),
    ("Kothapally Vikram Rathod", "vikramrathod.k-29@scds.saiuniversity.edu.in"),
    ("Malli Ram", "ram.m-29@scds.saiuniversity.edu.in"),
    ("Boppana Pavan Sai", "pavansai.b-29@scds.saiuniversity.edu.in"),
    ("Pachabatla Sukhesh", "sukhesh.p-29@scds.saiuniversity.edu.in"),
    ("Kancherla Vinay", "vinay.k-29@scds.saiuniversity.edu.in"),
    ("Vuyyala Sri Chakradhar", "srichakradhar.v-29@scds.saiuniversity.edu.in"),
    ("Saijayni M S", "saijayni.m-29@scds.saiuniversity.edu.in")
]

SECTION_6_STUDENTS = [
    # Batch 1
    ("Doggireddy Saiharshith Reddy", "saiharshithreddy.d-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Palli Keerthana", "keerthana.p-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Gundra Sweenija Reddy", "sweenijareddy.g-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Padarthi Vishnu Vardhan Reddy", "vishnuvardhanreddy.p-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Pannem Uday Kumar", "udaykumar.p-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Maddala Mahesh Kumar Reddy", "maheshkumarreddy.m-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Kavali Madhu Sekhar Reddy", "madhusekharreddy.k-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Thudimella Venkata Likith", "venkatalikith.t-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Thiruvathuru Harsha Vardhan Rayulu", "harshavardhan.t-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Kolli Jeshvitha Reddy", "jeshvithreddy.k-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Syed Sameer Ahamed", "sameerahamed.s-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Buchupalle Siva Mohan Reddy", "sivamohanreddy.b-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Yanamala Goutham Reddy", "gowthamreddy.y-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Bochhu Nitya Sri", "nityasri.b-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Padarthi Thrigun Surya Saran Sreekar", "suryasaransreekar.p-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Veduruparthi Satya Bhaskara Varun", "satyabhaskaravarun.v-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Mahidhar Naidu Kommi", "mahidhar.k-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Dandamudi Rama Nikhita", "ramnikhita.d-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Tulluri Navadeep", "navadeep.t-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Jakkireddy Syam Sundar Pavan Kumar Reddy", "syamsundhar.j-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Lukkani Dheeraj", "dheeraj.l-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Edara Yashwanth Chowdary", "yashwanthchowdary.e-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Mettukuru Santhosh Reddy", "santhoshreddy.m-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Lakku Venkateswarlu", "venkateswarlu.l-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Pulipati Gowtham", "gowtham.p-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Tallu Venkata Mohan Reddy", "mohanreddy.t-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Nellore Sanjana", "sanjana.n-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Yeddula Manoj Kumar Reddy", "manojkumarreddy.y-29@scds.saiuniversity.edu.in", "SCDS"),
    ("M Sai Charan", "saicharan.m2-29@scds.saiuniversity.edu.in", "SCDS"),
    # Batch 2
    ("Netibottu Shaik Mahammad Hujefa", "mahammadhujefa.n-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Nodagala Devarshini Lakshmi Akshaya", "devarshinilakshmiakshaya.n-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Malli Lakshman", "lakshman.m-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Nakka Parimala", "parimala.n-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Bakka Mohith Venkata Ganesh Reddy", "ganeshreddy.b-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Jorige Kalyan Ram", "kalyanram.j-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Maramreddy Shiva Nandheswara Reddy", "shivanandheswarareddy.m-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Sura Bhavana", "bhavana.s-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Nare Sandhya", "sandhya.n-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Chinna Nagappagari Mounika", "mounika.c-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Padarthi Sahithi", "sahithi.p-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Baira Spoorthi", "spoorthi.b-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Malireddy Mineesh", "mineesh.m-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Boodati Jayanth", "jayanth.b-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Palagiri Jeswith Venkata Sai", "jeswithvenkatasai.p-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Tippuluri Safiya", "safiya.t-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Madarapu Jaswanth", "jaswanth.m-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Baddigam Venkateswara Reddy", "venkateswarareddy.b-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Dandela Sri Charan Kumar Reddy", "charankumar.d-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Anamala Hemanth Kumar", "hemanthkumar.a-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Katha Venkata Nishanth Reddy", "venkatanishanthreddy.k-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Santimalla Nihitha", "nihitha.s-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Thalliboyina Sashank", "sashank.t-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Pabolu Vyshnavi Anantha Lakshmi", "vyshnaviananthalakshmi.p-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Gummalla Venkata Santosh Reddy", "santhoshreddy.g-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Sangala Sai Teja", "saiteja.s-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Koppula Venkata Sai Kishore", "venkatasaikishore.k-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Byrugani Ragavarshini", "ragavarshini.b-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Janga Muni Bhargav Reddy", "bhargavreddy.j-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Podalakuru Bindu Lovely", "bindulovely.p-29@scds.saiuniversity.edu.in", "SCDS"),
    # Batch 3
    ("Baira Kushi", "kushi.b-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Kanam Chandu", "chandu.k-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Bakkisetty Tarun", "tarun.b-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Podapati Sasidhar", "sasidhar.p-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Rayi Manvitha Rai", "manvitharaj.r-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Tankasala Geethika", "geethika.t-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Bovilla Meganadh Reddy", "meghanadhreddy.b-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Abhiram Thandra", "abhiram.t-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Vasili Hemal Ankeswar", "hemalankeswar.v-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Ravipati Kouhik Sri Ram", "kowshiksriram.r-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Kesamsetty Shanmukha Lakshmi", "shanmukhalakshmi.k-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Ravipati Rajesh", "rajesh.r-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Maddala Haricharan Reddy", "haricharanreddy.m-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Peddireddy Siva Kumar Reddy", "sivakumarreddy.p-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Chamarthi Karthik Varma", "karthikvarma.c-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Sannareddy Mohitha Reddy", "mohitha.s-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Konakalla Sri Purna Akshith", "puranakshith.k-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Kandrati Tejomai", "tejoamai.k-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Battula Bharath Kumar Reddy", "barathkumar.r-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Meha E", "meha.e-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Thugu Harshavardhan Reddy", "harshavardhan.t1-29@scds.saiuniversity.edu.in", "SCDS"),
    ("J L Dhanush", "dhanush.j-29@scds.saiuniversity.edu.in", "SCDS"),
    ("Tadikela Sandeep Kumar", "sandeepkumar.t-29@soai.saiuniversity.edu.in", "SOAI")
]

# =====================================================================
# SEED FUNCTIONS
# =====================================================================

def seed_school():
    print("Seeding schools...")
    scds = School(
        name='School of Computing and Data Science',
        code='SCDS',
        domain='scds.saiuniversity.edu.in'
    )
    # Adding global universities if needed
    sas = School(name='School of Arts and Sciences', code='SAS', domain='sas.apex.edu.in')
    sol = School(name='School of Law', code='SOL', domain='sol.apex.edu.in')
    soai = School(name='School of AI', code='SOAI', domain='soai.saiuniversity.edu.in')
    
    db.session.add_all([scds, sas, sol, soai])
    db.session.commit()
    return scds, soai

def seed_staff(school):
    print("Seeding staff...")
    pw = bcrypt.generate_password_hash('hive@1234').decode('utf-8')
    
    # Global Admin
    admin = User(school_id=None, email='admin@saiuniversity.edu.in',
                 password_hash=pw, role='admin', name='System Admin')
    # Superadmin
    superadmin = User(school_id=None, email='superadmin@saiuniversity.edu.in',
                      password_hash=pw, role='superadmin', name='Super Admin')
    
    # SCDS Staff
    dean = User(school_id=school.id, email='dean@scds.saiuniversity.edu.in',
                password_hash=pw, role='dean', name='Dr. Sarah Dean')
    prof = User(school_id=school.id, email='professor@scds.saiuniversity.edu.in',
                password_hash=pw, role='professor', name='Prof. Nitish Rana')
    assistant = User(school_id=school.id, email='assistant@scds.saiuniversity.edu.in',
                     password_hash=pw, role='assistant_professor', name='Asst. Prof. Alex')
    
    db.session.add_all([admin, superadmin, dean, prof, assistant])
    db.session.commit()
    
    # Add profiles
    db.session.add_all([
        Teacher(user_id=prof.id, department='Computer Science'),
        Teacher(user_id=assistant.id, department='Computer Science')
    ])
    db.session.commit()
    return prof

def seed_section_1(school):
    print("Seeding Section 1 students...")
    sec = Section(school_id=school.id, name='Section 1', code='SCDS-CS-S1', batch_year=2025)
    db.session.add(sec)
    db.session.commit()
    
    pw = bcrypt.generate_password_hash('hive@1234').decode('utf-8')
    for s_data in SECTION_1_STUDENTS:
        user = User(school_id=school.id, email=s_data['email'],
                    password_hash=pw, role='student', name=s_data['name'], must_change_password=True)
        db.session.add(user)
        db.session.flush()
        
        student = Student(user_id=user.id, section_id=sec.id, enrollment_year=2025, major='Computer Science')
        db.session.add(student)
    db.session.commit()

def seed_section_2(school):
    print("Seeding Section 2 students...")
    sec = Section(school_id=school.id, name='Section 2', code='SCDS-CS-S2', batch_year=2025)
    db.session.add(sec)
    db.session.commit()
    
    pw = bcrypt.generate_password_hash('hive@1234').decode('utf-8')
    for name, email in SECTION_2_STUDENTS:
        user = User(school_id=school.id, email=email,
                    password_hash=pw, role='student', name=name, must_change_password=True)
        db.session.add(user)
        db.session.flush()
        
        student = Student(user_id=user.id, section_id=sec.id, enrollment_year=2025, major='Computer Science')
        db.session.add(student)
    db.session.commit()

def seed_section_3(school):
    print("Seeding Section 3 students...")
    sec = Section(school_id=school.id, name='Section 3', code='SCDS-CS-S3', batch_year=2025)
    db.session.add(sec)
    db.session.commit()
    
    pw = bcrypt.generate_password_hash('hive@1234').decode('utf-8')
    for i, (name, email) in enumerate(SECTION_3_STUDENTS):
        # Rows 75-85 (indices 74-84) get lab_section=8, others lab_section=3
        lab_sec = 8 if i >= 74 else 3
        
        user = User(school_id=school.id, email=email,
                    password_hash=pw, role='student', name=name, must_change_password=True)
        db.session.add(user)
        db.session.flush()
        
        student = Student(user_id=user.id, section_id=sec.id, enrollment_year=2025, 
                          major='Computer Science', lab_section=lab_sec)
        db.session.add(student)
    db.session.commit()
    return sec

def seed_section_5(school):
    print("Seeding Section 5 students...")
    sec = Section(school_id=school.id, name='Section 5', code='SCDS-CS-S5', batch_year=2025)
    db.session.add(sec)
    db.session.commit()
    
    pw = bcrypt.generate_password_hash('hive@1234').decode('utf-8')
    for name, email, lab_sec in SECTION_5_STUDENTS:
        user = User(school_id=school.id, email=email,
                    password_hash=pw, role='student', name=name, must_change_password=True)
        db.session.add(user)
        db.session.flush()
        
        student = Student(user_id=user.id, section_id=sec.id, enrollment_year=2025, major='Computer Science', lab_section=lab_sec)
        db.session.add(student)
    db.session.commit()

def seed_timetable(school, section_3, teacher_user):
    print("Seeding courses and timetable...")
    
    # Courses for Section 3
    courses_to_create = [
        ("Discrete Mathematics", "CS-301", 4),
        ("Indian Constitution and Democracy", "ICD-101", 2),
        ("Python and Data Structure (LAB)", "CS-302L", 2),
        ("Introduction to Data Structures", "CS-302", 4),
        ("Environment and Sustainability", "ES-101", 2),
        ("Programming in Python", "CS-303", 4),
    ]
    
    section_courses = {}
    for name, code, credits in courses_to_create:
        course = Course(
            section_id=section_3.id,
            name=name,
            code=code,
            teacher_id=teacher_user.id,
            credits=credits
        )
        db.session.add(course)
        db.session.flush()
        section_courses[name] = course

    # Timetable data for Section 3
    entries_data = [
        # Monday
        (0, "10:40 AM", "12:10 PM", "Discrete Mathematics", "AB2 - 203", "#cfe2f3"),
        (0, "02:15 PM", "03:40 PM", "Indian Constitution and Democracy", "AB2 - 202", "#ead1dc"),
        (0, "03:50 PM", "05:15 PM", "Python and Data Structure (LAB)", "Computer Lab - AB1 - First Floor", "#b45f06"),
        # Tuesday
        (1, "09:00 AM", "10:30 AM", "Introduction to Data Structures", "AB1 - 101", "#f9cb9c"),
        (1, "12:15 PM", "01:45 PM", "Environment and Sustainability", "AB1 - Moot Court Hall", "#d9ead3"),
        # Wednesday
        (2, "09:00 AM", "10:30 AM", "Discrete Mathematics", "AB2 - 203", "#cfe2f3"),
        (2, "02:15 PM", "03:40 PM", "Indian Constitution and Democracy", "AB2 - 207", "#ead1dc"),
        # Thursday
        (3, "09:00 AM", "10:30 AM", "Programming in Python", "AB2 - 207", "#fce5cd"),
        (3, "12:20 PM", "01:40 PM", "Python and Data Structure (LAB)", "Computer Lab - AB1 - First Floor", "#b45f06"),
        # Friday
        (4, "10:40 AM", "12:10 PM", "Programming in Python", "AB2 - 202", "#fce5cd"),
        (4, "02:15 PM", "03:40 PM", "Introduction to Data Structures", "AB2 - 202", "#f9cb9c"),
        (4, "03:50 PM", "05:15 PM", "Environment and Sustainability", "AB2 - 202", "#d9ead3"),
    ]

    for day, start, end, title, room, color in entries_data:
        course = section_courses.get(title)
        entry = TimetableEntry(
            section_id=section_3.id,
            course_id=course.id if course else None,
            day=day,
            start_time=start,
            end_time=end,
            title=title,
            teacher=teacher_user.name,
            room=room,
            color=color,
            status='active'
        )
        db.session.add(entry)
    db.session.commit()

def seed_section_4(school):
    print("Seeding Section 4 students...")
    sec = Section(school_id=school.id, name='Section 4', code='SCDS-CS-S4', batch_year=2025)
    db.session.add(sec)
    db.session.commit()
    
    pw = bcrypt.generate_password_hash('hive@1234').decode('utf-8')
    for name, email in SECTION_4_STUDENTS:
        user = User(school_id=school.id, email=email,
                    password_hash=pw, role='student', name=name, must_change_password=True)
        db.session.add(user)
        db.session.flush()
        
        student = Student(user_id=user.id, section_id=sec.id, enrollment_year=2025, major='Computer Science')
        db.session.add(student)
    db.session.commit()

def seed_section_6(scds_school, soai_school):
    print("Seeding Section 6 students...")
    sec = Section(school_id=scds_school.id, name='Section 6', code='SCDS-CS-S6', batch_year=2025)
    db.session.add(sec)
    db.session.commit()
    
    pw = bcrypt.generate_password_hash('hive@1234').decode('utf-8')
    for name, email, school_code in SECTION_6_STUDENTS:
        target_school = scds_school if school_code == "SCDS" else soai_school
        if not target_school:
            print(f"Warning: School {school_code} not found for student {name}.")
            continue
            
        user = User(school_id=target_school.id, email=email,
                    password_hash=pw, role='student', name=name, must_change_password=True)
        db.session.add(user)
        db.session.flush()
        
        student = Student(user_id=user.id, section_id=sec.id, enrollment_year=2025, major='Computer Science')
        db.session.add(student)
    db.session.commit()

def seed_all():
    scds_school, soai_school = seed_school()
    prof = seed_staff(scds_school)
    seed_section_1(scds_school)
    seed_section_2(scds_school)
    secin3 = seed_section_3(scds_school)
    seed_section_4(scds_school)
    seed_section_5(scds_school)
    seed_section_6(scds_school, soai_school)
    seed_timetable(scds_school, secin3, prof)
    print("All data seeded successfully.")

if __name__ == "__main__":
    with app.app_context():
        print("Dropping and recreating all tables for a fresh seed...")
        db.metadata.drop_all(bind=db.engine)
        db.create_all()
        seed_all()
        print("Database initialized successfully.")
