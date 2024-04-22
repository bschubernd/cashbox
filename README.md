# cashbox - calculate cost of articles
cashbox is a Gtk4 app to calculate cost of articles.
It can be used by small clubs on a celebration,
to memorise the cost of sold articles
and to calculate the price and change.

## main windows
 * Pricelist - edit list of articles (name, price and optional count)
 * Sale - selects articles
 * Receipt - shows cost of selected articles
 
## work flow
1. optionally scan price-list with ocr software (outside of cashbox)

2. edit price-lsit with cashbox-Pricelist
 * empty lines in the price-list are ignored
 * each line represents one article
 * each line has the format: `<name> <price> [<count>]`
 * `<name>` can have spaces but must be unique.
 * `<price>` must be one ore more digits followed by a decimal separator and 2 decimal places
 * `<count>` must be one or more digits and is optional.

3. select, deselect or modify count of articles with cashbox-Sale

4. present cost of articles and calculate change

# pictures


![about cashbox](pics/about-details.png)

![pricelist empty](pics/pricelist-empty.png)

![pricelist help workflow](pics/pricelist-help-workflow.png)

![pricelist with data](pics/pricelist-correct.png)

![sale select](pics/Sale-select.png)

![sale inclrease count ](pics/sale-increase-count.png)

![receipt sum](pics/receipt-sum.png)

![receipt show return](pics/receipt-show-return.png)
