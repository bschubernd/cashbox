# cashbox - memorise cost and calculate price of articles
cashbox is a Gtk4 app tested on the librem5 with mobian.

cashbox memorises the cost of articles and calculates the total price and
change. It is intended for small clubs on a celebration, where members are
not experienced in memorizing prices and doing mental arithmetic.

## main windows
 * Pricelist - edit list of articles (name, price and optional count)
 * Sale - selects articles
 * Receipt - shows cost of selected articles
 
## work flow
1. optionally scan price-list with ocr software (outside of cashbox)

2. edit price-lsit with cashbox-Pricelist
 * empty lines in the price-list are ignored
 * comments starting with a '#' are ignored
 * each line represents one article
 * each line has the format: `<name> <price> [<count>]`
 * `<name>` can have spaces but must be unique.
 * `<price>` must be one ore more digits followed by a decimal separator and 2 decimal places
 * `<count>` must be one or more digits and is optional.

3. select, deselect or modify count of articles with cashbox-Sale

4. present cost of articles and calculate change

## testing cashbox

cashbox can now be installed from debian (https://packages.debian.org/cashbox)

## pictures

![about cashbox](pics/about.png)

![about cashbox details](pics/about-details.png)

![pricelist empty](pics/pricelist-empty.png)

![pricelist help workflow](pics/pricelist-help-workflow.png)

![pricelist with data](pics/pricelist-correct.png)

![sale select](pics/Sale-select.png)

![sale inclrease count ](pics/sale-increase-count.png)

![receipt sum](pics/receipt-sum.png)

![receipt show return](pics/receipt-show-return.png)

