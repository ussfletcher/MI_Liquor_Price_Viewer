''' This program was created to view statistics based on information provided by 
    the Michigan State Liquor Control Commission.
    The text file is located at: http://www.dleg.state.mi.us/mlcc/pricebook/webprbk.txt
    Inforrmation about parsing this file is at: http://www.michigan.gov/documents/CIS_LCC_fdcdftp_43429_7.pdf
'''
import optparse
import urllib2
import operator


''' The website where this information is stored
'''
WEBSITE_URL = r"http://www.dleg.state.mi.us/mlcc/pricebook/webprbk.txt"

''' The data we are parsing are stored in fixed-width values given by the following:
    Columns        Item                Columns        Item
    0-4            Liquor code          122-124       Pack Size
    5-36           Brand Name           125-132       On Premise Price
    37-39          ADA Num              133-140       Off Premise Price
    40-64          ADA Name             141-148       Shelf Price
    65-89          Vendor Name          149-162       Global Trade Item Num1
    90-109         Liquor Type          163-176       Global Trade Item Num2
    110-114        Proof                177-184       Effective Date MMDDCCYY
    115-122        Bottle Size (always ML, so we can drop the units or last 2 chars)
    
    For our purposes we are only going to focus on the Brand Name, Liquor Type, Proof,
    Bottle Size, and Shelf Price.
    
'''    
offsets = { 'liq_code':(0,5),'br_name':(5,36),'ada_num':(37,39),'ada_name':(40,64), \
            'vend_name':(65,89), 'liq_type':(90,109), 'proof':(110,114),'bt_size':(115,120), \
            'pck_size':(122,124), 'on_premPrice':(125,132), 'off_premPrice':(133,140), \
            'shlf_price':(141,148), 'glbl_trdNum1':(149,162), 'glbl_trdNum2':(163,176), \
            'eff_date':(177,184)}


'''    This is the class that holds each type of liquor listed in the text document.
'''
class Booze:
    def __init__(self,input_str):
        global offsets
        '''    This is a neat Python introspection trick, you can access any of a class's instance 
            variables in a dictionary '__dict__'. so here we are making instance variables 
            dynamically from our input, and parsing the fixed column widths at the same time.
        '''
        for code,columns in offsets.iteritems():
            self.__dict__[code]=input_str[columns[0]:columns[1]]
            
        ''' Ok, now lets compute some interesting statistics, like ABV/price, total alcohol/price 
            and store those as well.
        '''
        self.price_perVol = round(float(self.shlf_price)/float(self.bt_size),3)
        self.price_perMlAlc = round((float(self.shlf_price)/(((float(self.proof)/2) / 100) * float(self.bt_size))),3)
        
    def __str__(self):
        return "%s\t\t%s\t%.1f\t%i mL\t$%.2f/btl\t\t$%.3f/mL\t$%.3f/mL of Alc." % (self.br_name, self.liq_type, \
                                                                float(self.proof), int(self.bt_size), \
                                                                float(self.shlf_price), self.price_perVol, \
                                                                self.price_perMlAlc)
    


        
''' Go out to the website where the text file is stored and retrieve a copy. With each line appended to a list.
'''
def get_prices():
    global WEBSITE_URL
    items = []
    try:
        data = urllib2.urlopen(WEBSITE_URL)
        for line in data:
            if len(line) > 0:
                items.append(line)
    except:
        print "Unable to parse website pricing data"
    return items

    '''    Simply iterate through a list and print the elements.
'''    
def print_list(list):
    for item in list:
        print item
'''    From the commandline the user can choose to sort our items by the different displayed fields.
'''    
if __name__ == '__main__':
    liquors = []
    items = get_prices()
    if len(items) < 1:
        print "Invalid price data"
    else:
        for item in items:
            liquors.append(Booze(item))
            
            
    parser = optparse.OptionParser()
    group = optparse.OptionGroup(parser, "Sorting methods")
    group.add_option("-p", "--price", action="store_const",const='shlf_price', dest='sort_method',
                        help="Sort by price (ascen)")
    group.add_option("-P", "--Proof", action="store_const",const='proof', dest='sort_method', \
                        help="Sort by Proof (ascen)")
    group.add_option("-v", "--volume", action="store_const",const='bt_size', dest='sort_method', \
                        help="Sort by volume (ascen)")
    group.add_option("-t", "--type", action="store_const",const='liq_type', dest='sort_method', \
                        help="Sort by type")
    group.add_option("-n", "--name", action="store_const",const='br_name', dest='sort_method', \
                        default="br_name", help="Sort by name")
    group.add_option("-V", action="store_const",const='price_perVol', dest='sort_method', \
                        help="Sort by Price/Volume (ascen)")
    group.add_option("-a", action="store_const",const='price_perMlAlc', dest='sort_method', \
                        help="Sort by Price/Quantity of Alcohol (ascen)")
    parser.add_option_group(group)
    (options, args) = parser.parse_args()
    
    
    
    liquors.sort(key=operator.attrgetter(options.sort_method))
    print_list(liquors)


