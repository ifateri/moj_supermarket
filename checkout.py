import pandas as pd

# function to apply buy one get one free to any product
def buy_one_get_one_free(count, price):
    if count.item() % 2 == 0:
        return price.item() * count.item() / 2
    else:
        temp = int(count.item() / 2) + 1 
        return temp * price.item()   

# function to apply bulk buy discount to any product
def bulk_buy_discount(count, price, threshold=3, discounted_price=4.50):
    if count.item() >= threshold:
        return count.item() * discounted_price
    else:
        return count.item() * price.item()

class Checkout:        
    def __init__(self):
        self.product_range = pd.DataFrame({
            'product_code': ['FR1', 'SR1', 'CF1'],
            'name': ['Fruit tea', 'Strawberries', 'Coffee'],
            'price': [3.11, 5.00, 11.23]})
        self._basket_items = None
        self._basket_total = None
    
    @property
    def basket_items(self):
        if self._basket_items is None:
            raise AttributeError('There are no items in your basket')
        else: return self._basket_items

    def scan_item(self, item):
        if self._basket_items is None:
            self._basket_items = []
            self._basket_items.append(item)
        else: self._basket_items.append(item)    
      
    def checkout(self):
        basket_df = (
            pd.DataFrame(self._basket_items, columns=['name'])
            .groupby('name', as_index=False)
            .agg(count=('name', 'size'))
            .merge(self.product_range, on='name', how='left')
            .assign(total=lambda x: x['count'] * x['price'])
        )

        # test whether basket contains fruit tea and strawberries
        if (basket_df['name'].str.contains('Fruit tea').any() 
                and basket_df['name'].str.contains('Strawberries').any()):
            # apply rule for fruit tea first
            fruit_tea = basket_df['name'].str.contains('Fruit tea')
            fruit_tea_subset = basket_df[fruit_tea]
            basket_df.loc[fruit_tea, 'total'] = buy_one_get_one_free(
                fruit_tea_subset['count'], fruit_tea_subset['price']
            )
            # apply rule for strawberries
            strawberries = basket_df['name'].str.contains('Strawberries')
            strawberries_subset = basket_df[strawberries]
            basket_df.loc[strawberries, 'total'] = bulk_buy_discount(
                strawberries_subset['count'], strawberries_subset['price']
            )

            return basket_df            

        # just fruit tea
        elif basket_df['name'].str.contains('Fruit tea').any():
                fruit_tea = basket_df['name'].str.contains('Fruit tea')
                fruit_tea_subset = basket_df[fruit_tea]
                basket_df.loc[fruit_tea, 'total'] = buy_one_get_one_free(
                    fruit_tea_subset['count'], fruit_tea_subset['price']
                )
                return basket_df

        # just strawberries
        elif basket_df['name'].str.contains('Strawberries').any():
            strawberries = basket_df['name'].str.contains('Strawberries')
            strawberries_subset = basket_df[strawberries]
            basket_df.loc[strawberries, 'total'] = bulk_buy_discount(
                strawberries_subset['count'], strawberries_subset['price']
            )
            return basket_df 

        # no offers on products selected
        else: 
            return basket_df

    def total(self):
        return self.checkout()['total'].sum()

    def add_to_product_range(self, product_code, name, price):
        temp_df = pd.DataFrame({
            'product_code': [f'{product_code}'],
            'name': [f'{name}'],
            'price': [f'{price}']
            })

        self.product_range = pd.concat(
            [self.product_range, temp_df],
            ignore_index=True,
        )