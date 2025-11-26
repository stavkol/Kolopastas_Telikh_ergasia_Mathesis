# -*- coding: utf-8 -*-
"""
Created on Wed Nov 26 13:20:52 2025

@author: user
"""

# mathesis.cup.gr
# N.  Αβούρης: Εισαγωγή στην Python
# Μάθημα 21.  Τελική εργασία
# mynews
'''
H γνωστή ειδησεογραφική ιστοσελίδα in. gr διαθέτει υπηρεσία απευθείας αναφοράς ειδήσεων για
διάφορες κατηγορίες με μορφή rss (rss. in.gr). Ζητείται να κατασκευάσετε μια εφαρμογή που
ενημερώνει τον χρήστη για ειδήσεις με βάση τα ενδιαφέροντά του.
1. Κάθε χρήστης ορίζει τα θέματα που τον ενδιαφέρουν και για κάθε κατηγορία αν το επιθυμεί
ορίζει συγκεκριμένους όρους αναζήτησης. 
Οι επιθυμίες των χρηστών αποθηκεύονται σε αρχείο users.csv
3. Κάθε φορά που ξεκινάει η εφαρμογή αναζητάει για τον συγκεκριμένο χρήστη νεότερες ειδήσεις
με βάση τα ενδιαφέροντά του.
4. Οι ειδήσεις εμφανίζονται αρχικά ως τίτλοι, και στη συνέχεια ο χρήστης μπορεί να επιλέξει
αυτές που επιθυμεί να δει με λεπτομέρειες.
5. Η εφαρμογή θα πρέπει να υποστηρίζει τη διαχείριση χρηστών και των προφίλ τους.
'''

import os. path
import urllib.request
import urllib.error
import re
import datetime
import util
# τα ονόματα βοηθητικών αρχείων
data_dir = os.getcwd() # ο φάκελος για αποθήκευση δεδομένων εφαρμογής
feeds_file = os.path.join(data_dir, 'news.csv') # αρχείο με κατηγορίες από rss feeds
users_file = os.path.join(data_dir, 'users.csv') # αρχείο με προφιλ χρηστών
WIDTH = 70  #πλάτος κειμένου είδησης
URL = "http://rss.in.gr/" # διεύθυνση ειδήσεων
# καθολική μεταβλητή
user = {} # καθολική μεταβλητή που περιέχει τα στοιχεία του συνδεδεμένου κάθε φορά χρήστη
# στη μορφή: user = {'user': 'nikos', 'areas': {'Ειδήσεις Πολιτισμός': ['Καζαντζάκη'], 'Υγεία': []}

def login_user():
    '''
    ΕΡΩΤΗΜΑ 1
    H συνάρτηση ζητάει από τον χρήστη το username
    Αν ο χρήστης δεν δώσει όνομα επιστρέφει την τιμή False
    Αν δώσει τη λέξη admin καλείται η συνάρτηση admin() διαχείρισης χρηστών
    Aν δώσει όνομα, ελέγχει αν αυτός υπάρχει ήδη καλώντας τη συνάρτηση retrieve_user(username)
        αν η retrieve_user() επιστρέψει True (βρέθηκε χρήστης) τότε τυπώνει ένα μήνυμα καλωσορίσματος και
        επιστρέφει την τιμή True
        αν η retrieve_user() επιστρέψει False (δεν βρέθηκε χρήστης) τότε ρωτάει τον χρήστη αν θέλει να
        δημιουργήσει προφίλ,
            αν ο χρήστης απαντήσει θετικά, καλείται η συνάρτηση update_user() η οποία αποθηκεύει
                                το προφίλ του χρήστη στο αρχείο users_file, και επιστρέφει True,
            αλλιώς επιστρέφει False
    '''
    global user
    username = input('Δώστε το όνομα χρήστη σας: ')
    
    # Αν δεν δώσει όνομα
    if not username:
        return False
    
    # Αν δώσει admin
    if username. lower() == 'admin':
        admin()
        return False
    
    # Έλεγχος αν υπάρχει ο χρήστης
    if retrieve_user(username):
        print(f'Καλώς ήρθες {username}!')
        return True
    else:
        # Δεν βρέθηκε ο χρήστης
        reply = input(f'Ο χρήστης {username} δεν υπάρχει. Θέλετε να δημιουργήσετε προφίλ; (ναι/όχι) ')
        if reply and reply[0].lower() in 'νy':
            # Δημιουργία νέου χρήστη με κενό προφίλ
            user = {'user': username, 'areas': {}}
            update_user()
            print(f'Το προφίλ του χρήστη {username} δημιουργήθηκε!')
            return True
        else:
            return False

def admin():
    '''
    ΕΡΩΤΗΜΑ 2.  Συνάρτηση που δημιουργεί και διαγράφει χρήστες (λειτουργίες διαχειριστή). 
    Φορτώνει το αρχείο χρηστών και επαναληπτικά ρωτάει τον διαχειριστή αν θέλει να διαγράψει ή να προσθέσει χρήστες.
    Αν ο διαχειριστής διαγράψει έναν χρήστη, αυτός αφαιρείται από το αρχείο χρηστών.
    Αν ο διαχειριστής προσθέσει ένα χρήστη, αυτός προστίθεται με κενό προφίλ στο αρχείο χρηστών.
    Η συνάρτηση χρησιμοποιεί τις βοηθητικές συναρτήσεις του αρχείου util.py
    Δεν επιστρέφει τιμή. 
    '''
    print('*** ΛΕΙΤΟΥΡΓΙΕΣ ΔΙΑΧΕΙΡΙΣΤΗ ***')
    
    while True:
        # Φόρτωση αρχείου χρηστών
        if os.path.isfile(users_file):
            users_list = util.csv_to_dict(users_file)
        else:
            users_list = []
        
        # Εμφάνιση υπαρχόντων χρηστών
        print('\nΥπάρχοντες χρήστες:')
        if users_list:
            usernames = list(set([u['user'] for u in users_list]))
            for i, username in enumerate(usernames):
                print(f'{i+1}. {username}')
        else:
            print('Δεν υπάρχουν χρήστες')
        
        # Επιλογή ενέργειας
        action = input('\n(Π)ροσθήκη χρήστη, (Δ)ιαγραφή χρήστη, (Έ)ξοδος: ')
        
        if not action or action[0].upper() in 'ΈE':
            break
        elif action[0].upper() in 'ΠP':
            # Προσθήκη χρήστη
            new_user = input('Όνομα νέου χρήστη: ')
            if new_user:
                # Έλεγχος αν υπάρχει ήδη
                existing = [u for u in users_list if u['user'] == new_user]
                if existing:
                    print(f'Ο χρήστης {new_user} υπάρχει ήδη!')
                else:
                    # Προσθήκη με κενό προφίλ
                    users_list.append({'user': new_user, 'area': '', 'keywords': ''})
                    util.dict_to_csv(users_list, users_file)
                    print(f'Ο χρήστης {new_user} προστέθηκε!')
        elif action[0].upper() in 'ΔD':
            # Διαγραφή χρήστη
            del_user = input('Όνομα χρήστη προς διαγραφή: ')
            if del_user:
                # Αφαίρεση όλων των εγγραφών του χρήστη
                users_list = [u for u in users_list if u['user'] != del_user]
                util.dict_to_csv(users_list, users_file)
                print(f'Ο χρήστης {del_user} διαγράφηκε!')

def retrieve_user(username):
    '''
    ΕΡΩΤΗΜΑ 3
    :param username: το όνομα χρήστη που έδωσε ο χρήστης
    :return: True αν ο χρήστης βρέθηκε στο αρχείο users_file.  Στην περίπτωση αυτή στην καθολική μεταβλήτη
    user φορτώνεται το λεξικό που περιέχει τα στοιχεία του χρήστη, για παράδειγμα:
    {'user': 'nikos',
     'areas': { 'Ειδήσεις Πολιτισμός': ['Καζαντζάκη'],
                'Υγεία': []
                }
    Προσοχή: αν ένα θέμα περιέχει πολλούς όρους, αυτοί έχουν αποθηκευτεί ως μια συμβολοσειρά με το $ ως
    διαχωριστικό.  Συνεπώς πρέπει εδώ να τους διαχωρίσουμε και να τους εισάγουμε στη σχετική λίστα όρων.
    Η συνάρτηση επιστρέφει False αν δεν υπάρχει ο χρήστης ήδη στο αρχείο users_file
    '''
    global user
    
    # Έλεγχος αν υπάρχει το αρχείο
    if not os.path.isfile(users_file):
        return False
    
    # Φόρτωση αρχείου χρηστών
    users_list = util.csv_to_dict(users_file)
    
    # Αναζήτηση χρήστη
    user_records = [u for u in users_list if u['user'] == username]
    
    if not user_records:
        return False
    
    # Δημιουργία λεξικού χρήστη
    user = {'user': username, 'areas': {}}
    
    for record in user_records:
        area = record['area']
        keywords_str = record['keywords']
        
        # Διαχωρισμός όρων με βάση το $
        if keywords_str:
            keywords_list = keywords_str.split('$')
        else:
            keywords_list = []
        
        user['areas'][area] = keywords_list
    
    return True

def update_user():
    '''
    ΕΡΩΤΗΜΑ 4
    H συνάρτηση αυτή αποθηκεύει το περιεχόμενο της καθολικής μεταβλητής user στο αρχείο users_file
    Προσέχουμε ώστε αν στο αρχείο users_file υπάρχουν ήδη άλλοι χρήστες αυτοί πρώτα ανακτώνται, προστίθεται
    στη συνέχεια ο χρήστης user και τέλος αποθηκεύονται όλοι οι χρήστες ξανά στο users_file. 
    Επίσης προσέχουμε ώστε οι όροι αναζήτησης που υπάρχουν για κάποιο θέμα να αποθηκευτούν ως μια
    συμβολοσειρά με τον χαρακτήρα $ ως διαχωριστικό. 
    Επιστρέφει None
    '''
    # Φόρτωση υπαρχόντων χρηστών
    if os.path.isfile(users_file):
        users_list = util.csv_to_dict(users_file)
    else:
        users_list = []
    
    # Αφαίρεση παλιών εγγραφών του τρέχοντος χρήστη
    users_list = [u for u in users_list if u['user'] != user['user']]
    
    # Προσθήκη νέων εγγραφών του χρήστη
    for area, keywords_list in user['areas'].items():
        # Ένωση όρων με $
        keywords_str = '$'. join(keywords_list)
        users_list.append({
            'user': user['user'],
            'area': area,
            'keywords': keywords_str
        })
    
    # Αποθήκευση στο αρχείο
    util.dict_to_csv(users_list, users_file)


def load_newsfeeds():
    '''
    Η συνάρτηση φορτώνει τις διευθύνσεις των rss feed urls στο λεξικό feeds από το σχετικό αρχείο
    επιστρέφει το λεξικό που ανακτάται ή επιστρέφει False αν το αρχείο feeds_file δεν υπάρχει
    '''
    if os.path.isfile(feeds_file) :
        return util.csv_to_dict(feeds_file)
    else:
        print('Δεν υπάρχει αρχείο {}'.format(feeds_file))
        return False

def load_news_to_temp(feeds):
    '''
    Άνοιγμα του rss feed,
    :param feeds οι θεματικές περιοχές ειδήσεων με τις αντίστοιχες διευθύνσεις των rss feeds
    φορτώνει τα άρθρα και τα αποθηκεύει σε προσωρινό αρχείο
    '''
    count = 0
    news_items = []
    for area in user['areas']:
        print(area, ' .... ', end='')
        url = [x['rss'] for x in feeds if x['title'] == area]
        if url:
            url = url[0]
            req = urllib.request.Request(url)
        try:
            with urllib.request.urlopen(req) as response:
                html = response.read().decode()
            filename = "tempfile. rss"
            with open(filename, "w", encoding="utf-8") as p:
                p.write(html)
        except urllib.error.HTTPError as e:
            print(e.code)
            print(e.readline())
        except urllib.error.URLError as e:
            print(e)
            if hasattr(e, 'reason'):  # χωρίς σύνδεση ιντερνετ
                print('Αποτυχία σύνδεσης στον server')
                print('Αιτία: ', e.reason)
        else:
            with open(filename, 'r', encoding='utf-8') as f:
                rss = f.read(). replace("\n", " ")
                items = re.findall(r"<item>(.*?)</item>", rss, re.MULTILINE | re.IGNORECASE)
                count_area_items = 0
                for item in items:
                    news_item = {}
                    title = re.findall(r"<title>(.*?)</title>", item, re.MULTILINE | re.IGNORECASE)
                    date = re.findall(r"<pubdate>(.*?)</pubdate>", item, re.MULTILINE | re.IGNORECASE)
                    if len(title) > 0:
                        title = title[0]
                    else: title = ''
                    date = format_date(date[0]) if date else ' '
                    content = re.findall(r"<description>(.*?)</description>", item, re.MULTILINE | re.IGNORECASE)
                    found = False
                    if user['areas'][area]:
                        for k in user['areas'][area]:
                            if check_keyword(k, title) or check_keyword(k, content[0]):
                                found = True
                                break
                    else: found = True
                    if found:
                        count += 1
                        count_area_items += 1
                        news_item = {'no':count, 'title': title, 'date':date, 'content': content[0]}
                        news_items.append(news_item)
                        if count> 99: break # μόνο 100 πρώτες ειδήσεις
                print(count_area_items, end= ' ,   ')
    util.dict_to_csv(news_items, 'mytemp.csv') # temporary store of news items
    print()
    return len(news_items)

def print_titles():
    '''
    Η συνάρτηση αυτή τυπώνει τους τίτλους των ειδήσεων που υπάρχουν στο αρχείο mytemp.csv
    :return:
    '''
    try:
        news_items = util.csv_to_dict('mytemp.csv')
        for item in news_items:
            print(item['no'] + ' [' + item['date'] + ']\t' + item['title'])
        return True
    except FileNotFoundError:
        return False

def print_news_item(item_no):
    '''
    ΕΡΩΤΗΜΑ 5. 
    Να γράψετε τη συνάρτηση που τυπώνει την είδηση με αριθμό item_no που βρίσκεται αποθηκευμένη στο αρχείο
    mytemp.csv. 
    Χρησιμοποιήστε την βοηθητική συνάρτηση formatted_print() για το σώμα της είδησης.
    Η συνάρτηση επιστρέφει True αν η είδηση βρέθηκε και τυπώθηκε, και False αν όχι
    '''
    try:
        news_items = util.csv_to_dict('mytemp.csv')
        
        # Αναζήτηση της είδησης με το συγκεκριμένο αριθμό
        for item in news_items:
            if int(item['no']) == item_no:
                print('\n' + WIDTH * '=')
                print(f"Είδηση {item['no']} - {item['date']}")
                print(item['title'])
                print(WIDTH * '-')
                formatted_print(item['content'])
                print(WIDTH * '=')
                return True
        
        # Αν δεν βρέθηκε η είδηση
        return False
    except FileNotFoundError:
        return False


def format_date(date):
    # βοηθητική συνάρτηση για διαμόρφωση της ημερομηνίας της είδησης
    m_gr = 'Ιαν Φεβ Μαρ Απρ Μαϊ Ιουν Ιουλ Αυγ Σεπ Οκτ Νοε ∆εκ'. split()
    m_en = 'Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split()
    d = re.findall(r"([0-9]{2}\s[A-Z][a-z]{2}\s[0-9]{4})",date, re.I)
    if d : date = d[0]. split()
    #if d: date = d. group(0).split()
    if date[1] in m_en: date[1] = m_gr[m_en.index(date[1])]
    return ' '.join(date)


def check_keyword(keyword, text):
    # βοηθητική συνάρτηση που αναζητάει το keyword σε μια συμβολοσειρά text.  Επιστρέφει True/False αν βρεθεί ή όχι. 
    tonoi = ('αά', 'εέ', 'ηή', 'ιί', 'οό', 'ύυ', 'ωώ')
    n_phrase= ''
    for c in keyword:
        char = c
        for t in tonoi:
            if c in t: char = '['+t+']'
        n_phrase += char
    pattern = r'.*'+n_phrase+r'.*'
    w =re.findall(pattern, text, re. I)
    if w:
        return True
    else:
        return False


def formatted_print(st, width=WIDTH):
    # συνάρτηση που τυπώνει συμβολοσειρά st με πλάτος width χαρακτήρων
    para = st.split("\n")
    for p in para:
        st = p. split()
        out = ""
        while True:
            while len(st) > 0 and len(out+st[0]) < width :
                out = " ". join([out, st. pop(0)])
            print(out)
            out = ""
            if len(st) == 0 : break


def manage_profile(feeds):
    global user
    modify = False
    while True:
        print_user_profile()
        print(WIDTH * '_')
        reply = input('Θέλετε να αλλάξετε το προφίλ σας; (Ναι για αλλαγές)')
        if not reply or reply[0].lower() not in 'νn': break
        print('Αρχικά θα μπορείτε να επιλέξετε από θέματα ειδήσεων, στη συνέχεια να ορίσετε όρους αναζήτησης σε κάθε θέμα')
        main_feeds = [x['title'] for x in feeds ]
        
        '''
        ΕΡΩΤΗΜΑ 6
        Επαναληπτικά ζητήστε από τον χρήστη να ορίσει τα θέματα ειδήσεων που τον ενδιαφέρουν
        '''
        while True:
            print_user_areas(main_feeds)
            print('\nΤα κύρια θέματα ειδήσεων είναι: ....  ')
            for i, feed in enumerate(main_feeds):
                print(f'{i}:{feed}')
            
            print_user_areas(main_feeds)
            choice = input('\nΜπορείτε να προσθέστε θέμα με +αριθμό ή να αφαιρέσετε με -αριθμό (enter για να συνεχίσετε)')
            
            if not choice:
                break
            
            # Επεξεργασία επιλογών
            choices = choice.split()
            for ch in choices:
                if ch. startswith('+'):
                    # Προσθήκη θέματος
                    try:
                        idx = int(ch[1:])
                        if 0 <= idx < len(main_feeds):
                            area = main_feeds[idx]
                            if area not in user['areas']:
                                user['areas'][area] = []
                                modify = True
                    except ValueError:
                        pass
                elif ch.startswith('-'):
                    # Αφαίρεση θέματος
                    try:
                        idx = int(ch[1:])
                        if 0 <= idx < len(main_feeds):
                            area = main_feeds[idx]
                            if area in user['areas']:
                                del user['areas'][area]
                                modify = True
                    except ValueError:
                        pass
        
        print_user_profile()
        print('\nΤώρα για κάθε θέμα ειδήσεων μπορείτε να επιλέξετε όρους αναζήτησης')
        
        '''
        ΕΡΩΤΗΜΑ 7
        Επαναληπτικά ζητήστε από τον χρήστη για κάθε θέμα ειδήσεων που τον ενδιαφέρει να προσθέσει ή να αφαιρέσει
        όρους αναζήτησης
        '''
        for area in user['areas']:
            while True:
                print(f'\nΘΕΜΑ:  {area}  ..  Όροι αναζήτησης: {user["areas"][area]}')
                choice = input('\nΜπορείτε να προσθέσετε ή να αφαιρέσετε όρους για κάθε θέμα με +λέξη, -λέξη... .(enter για να συνεχίσετε)')
                
                if not choice:
                    break
                
                # Επεξεργασία επιλογών
                choices = choice.split()
                for ch in choices:
                    if ch. startswith('+'):
                        # Προσθήκη όρου
                        keyword = ch[1:]
                        if keyword and keyword not in user['areas'][area]:
                            user['areas'][area].append(keyword)
                            modify = True
                    elif ch.startswith('-'):
                        # Αφαίρεση όρου
                        keyword = ch[1:]
                        if keyword in user['areas'][area]:
                            user['areas'][area].remove(keyword)
                            modify = True
        
        print_user_profile()
        reply = input('\n ...  Θέλετε άλλες αλλαγές στο προφίλ σας (ναι για αλλαγές))')
        if not reply or reply[0].lower() != 'ν': break
    if modify: # χρησιμοποιήστε μια λογική μεταβλητή η οποία γίνεται True αν ο έγιναν αλλαγές στο προφίλ του χρήστη
        update_user()


def print_user_areas(li):
    print('\nΤα ενδιαφέροντά σας είναι ... ', end='')
    items = False
    for item in li:
        if item in user['areas']. keys():
            print(item, end=', ')
            items = True
    if not items: print('ΚΑΝΕΝΑ ΕΝΔΙΑΦΕΡΟΝ', end='')
    print()

def print_user_profile():
    print('\nΤα θέματα ειδήσεων που σας ενδιαφέρουν είναι:')
    if not user['areas']: print('KENO ΠΡΟΦΙΛ ΧΡΗΣΤΗ')
    for area in user['areas']:
        print(area)
        for keyword in user['areas'][area]:
            print('\t\t', keyword)

def clear_temps():
    '''
    ΕΡΩΤΗΜΑ 8. 
    Να καθαρίσετε όποια βοηθητικά αρχεία έχουν δημιουργηθεί κατά τη διάρκεια εκτέλεσης του προγράμματος
    '''
    # Διαγραφή του mytemp.csv (δημιουργείται στη γραμμή 159)
    if os.path. isfile('mytemp.csv'):
        os.remove('mytemp.csv')
    
    # Διαγραφή του tempfile.rss (δημιουργείται στη γραμμή 120)
    if os.path.isfile('tempfile.rss'):
        os.remove('tempfile.rss')

def main():
    print("Σήμερα είναι :", str(datetime.datetime.today()). split()[0])
    username = login_user()
    if username:
        feeds = load_newsfeeds()
        if feeds:
            print('To mynews πρoσφέρει προσωποποιημένες ειδήσεις από το in. gr')
            while True: # main menu
                print(WIDTH * '=')
                user_selected = input('(Π)ροφίλ ενδιαφέροντα, (Τ)ίτλοι ειδήσεων, (enter)Εξοδος\n')
                if user_selected == '': # έξοδος
                    break
                elif user_selected.upper() in 'ΠP': # προφίλ
                    manage_profile(feeds) # διαχείριση του προφίλ χρήστη
                elif user_selected.upper() in 'ΤT': # παρουσίαση τίτλων ειδήσεων
                    if 'areas' in user. keys() and len(user['areas']) > 0 : # αν ο χρήστης έχει ορίσει areas
                        print_user_profile()
                        print('\nΤΕΛΕΥΤΑΙΕΣ ΕΙΔΗΣΕΙΣ ΠΟΥ ΣΑΣ ΕΝΔΙΑΦΕΡΟΥΝ... ΣΕ ΤΙΤΛΟΥΣ')
                        items_count = load_news_to_temp(feeds)  # φόρτωσε τις ειδήσεις που ενδιαφέρουν τον χρήστη
                        if items_count: # εαν υπάρχουν ειδήσεις σύμφωνα με το προφιλ του χρήστη ... 
                            print_titles() # τύπωσε τους τίτλους των ειδήσεων του χρήστη
                            while True:
                                print(WIDTH * '_')
                                item_no = input('Επιλογή είδησης (1 ..  {}) ή <enter> για να συνεχίσετε:'.format(items_count))
                                if item_no == '': break
                                if item_no.isdigit() and 0 < int(item_no) <= items_count:
                                    print_news_item(int(item_no))
                        else: print('Δεν υπάρχουν ειδήσεις με βάση το προφίλ ενδιαφερόντων σας .. .')
                    else: print('Πρέπει πρώτα να δημιουργήσετε το προφίλ σας')
    clear_temps()
    print('\nΕυχαριστούμε')


if __name__ == '__main__': main()