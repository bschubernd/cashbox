# cashbox - calculate cost of articles
cashbox is a Gtk4 app to calculate cost of articles
it can be used by small clubs on a celebration,
to memorise the cost of sold articles
and calculate the price and change.

## main windows
 * Pricelist - edit list of articles (name, price and optional count)
 * Sale - selects articles
 * Receipt - shows cost of selected articles
 
## work flow
1. optionally scan price-list with ocr software (outside of cashbox)

2. edit price-lsit with cashbox-Pricelist
 * empty lines in the price-list are ignored
 * each line represents one article
 * each line has the format: <name> <price> [<count>]
 * <name> can have spaces
 * <price> = digits[(.,)2-digits][<currency>]
 * <name> must be unique

3. select, deselect or modify count of articles with cashbox-Sale

4. present cost of articles and calculate change
