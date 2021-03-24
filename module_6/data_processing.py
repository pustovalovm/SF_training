# %%
import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt


class dataSet:
    def __init__(self, path, df: pd.DataFrame, is_test: bool):
        self.path = path
        self.dataframe = df
        self.is_test = is_test

    @classmethod
    def from_csv(cls, path_to_csv: str, is_test: bool):
        try:
            return cls(path_to_csv, pd.read_csv(
                path_to_csv,
                usecols=lambda x: x not in ('photos_links', 'descr')), is_test)
        except Exception as exc:
            print(f'Could not create dataset because of exception {exc}')
            return

    def fillna(self):
        if self.is_test:
            self.dataframe.drop(columns=['price'], inplace=True)
            self.dataframe.dropna(subset=['brand'], inplace=True)
            self.dataframe['views_total'].fillna(0, inplace=True)
        if not self.is_test:
            self.dataframe.dropna(subset=['price'], inplace=True)
            self.dataframe.dropna(subset=[
                'body_type', 'fuel_type', 'engine_volume',
                'engine_power', 'views_total',
                'owners_count', 'vin'],
                inplace=True)
        # self.dataframe.drop(columns=['views_today'], inplace=True)
        # self.dataframe.drop(columns=['vin'], inplace=True)
        # self.dataframe.drop(columns=['license_plate'], inplace=True)
        self.dataframe['generation'] = self.dataframe.generation.fillna(
            'Not Applicable')
        self.dataframe[['vin',
                        'license_plate',
                        'views_today']] = (self.dataframe[['vin',
                                                           'license_plate',
                                                           'views_today']]
                                           .fillna(''))
        self.dataframe.loc[(self.dataframe.pts.isna() == True) &
                           (self.dataframe.owners_count < 3),
                           'pts'] = 'Оригинал'
        self.dataframe.loc[(self.dataframe.pts.isna() == True) &
                           (self.dataframe.owners_count >= 3),
                           'pts'] = 'Дубликат'
        self.dataframe['exchange'] = self.dataframe.exchange.apply(
            lambda x: 1 if x == 'Рассмотрю варианты' else 0)
        self.dataframe['complectation'] = (self.dataframe.complectation
                                           .fillna(value='undefined'))
        if len(self.dataframe[self.dataframe.isna().any(axis=1)]) > 0:
            print('Остались незаполненные пропуски:'
                  f'\n{self.dataframe[self.dataframe.isna().any(axis=1)]}')

    def _get_test_filler(self, orig_frame_path):
        test_orig = pd.read_csv(orig_frame_path)
        brand_dict = dict(zip(
            sorted(test_orig.brand.unique()),
            sorted(self.dataframe.brand.unique())))
        test_orig['brand'] = test_orig['brand'].map(brand_dict)
        missing_links = list(set(test_orig.car_url)
                             - set(self.dataframe.url))
        test_filler = test_orig.query("car_url in @missing_links")
        formatted_filler = pd.DataFrame(columns=self.dataframe.columns)
        formatted_filler['brand'] = test_filler['brand']
        formatted_filler['model'] = test_filler['model_name']
        formatted_filler['offer_id'] = test_filler['sell_id']
        formatted_filler['year'] = test_filler['productionDate'].astype(int)
        formatted_filler['mileage'] = test_filler['mileage'].astype(float)
        formatted_filler['body_type'] = test_filler['bodyType']
        formatted_filler['color'] = test_filler['color']
        formatted_filler['fuel_type'] = test_filler['fuelType']
        formatted_filler['engine_volume'] = (test_filler['engineDisplacement']
                                             .apply(lambda x: float(x.split()[0]) if x != ' LTR' else 0))
        formatted_filler['engine_power'] = test_filler['enginePower'].apply(
            lambda x: float(x.split()[0]))
        formatted_filler['transmission'] = test_filler['vehicleTransmission']
        formatted_filler['wheel'] = test_filler['Руль']
        formatted_filler['state'] = test_filler['Состояние']
        formatted_filler['owners_count'] = test_filler['Владельцы'].apply(lambda x: x[0]).astype(int)
        formatted_filler['drive'] = test_filler['Привод']
        formatted_filler['pts'] = test_filler['ПТС']
        formatted_filler['customs'] = test_filler['Таможня']
        formatted_filler.reset_index(inplace=True, drop=True)
        formatted_filler.set_index(['brand'], inplace=True)
        formatted_filler.update(self.dataframe.groupby(['brand'])[
                                'photos_count'].median().astype(int), overwrite=False)
        formatted_filler.update(self.dataframe.groupby(['brand'])[
                                'views_total'].median(), overwrite=False)
        posted = self.dataframe.groupby(['brand'])['date_posted'].agg(
            pd.Series.mode).apply(lambda x: min(x) if len(x) < 5 else x)
        # костыль на случай нескольких мод
        formatted_filler.update(posted, overwrite=False)
        formatted_filler.update(self.dataframe.groupby(['brand'])[
                                'generation'].agg(pd.Series.mode), overwrite=False)
        formatted_filler.reset_index(inplace=True, drop=False)
        formatted_filler['complectation'] = 'undefined'
        formatted_filler['exchange'] = 0
        return formatted_filler

    def fill_missing_from_orig(self, orig_frame_path):
        if self.is_test:
            filler = self._get_test_filler(orig_frame_path)
            self.dataframe = self.dataframe.append(
                filler, ignore_index=True).reset_index(drop=True)
            self.dataframe['photos_count'] = self.dataframe['photos_count'].astype(int)
        else:
            print('Использовать только для теста!')
            return

    def reduce_train_to_test_models(self, test_brands, test_models):
        if not self.is_test:
            self.dataframe = self.dataframe.query('brand in @test_brands')
            self.dataframe = self.dataframe.query('model in @test_models')
        else:
            print('Это и так тест.')

    def _process_price(self):
        if not self.is_test:
            try:
                self.dataframe['log_price'] = self.dataframe.price.apply(
                    np.log)
                self.dataframe.drop(columns='price', inplace=True)
            except KeyError:
                print('Нет столбца с ценой, может она уже обработана?')
        else:
            print('У теста нет цен!')

    def _process_mileage(self):
        try:
            self.dataframe['log_mileage'] = self.dataframe.mileage.apply(
                np.log)
            self.dataframe.drop(columns='mileage', inplace=True)
        except KeyError:
            print('Нет столбца с пробегом, может он уже обработан?')

    def _reduce_photos_count(self, max_photos):
        self.dataframe = self.dataframe[self.dataframe.photos_count <
                                        max_photos]

    def _fix_fuel_type(self):
        self.dataframe['fuel_type'] = self.dataframe.fuel_type.str.lower()

    def _generate_complectation_dummies(self):
        return (pd.get_dummies(self.dataframe.complectation
                               .apply(lambda x: list(map(str.lower, x.split(','))))
                               .apply(pd.Series)
                               .stack())
                .sum(level=0))

    def _generate_dummies(self, dummies_list):
        return pd.get_dummies(self.dataframe[dummies_list])

    def prepare_frame_no_dummies(self,
                                 test_brands=None,
                                 test_models=None,
                                 orig_test_path=None):

        self.fillna()
        if self.is_test and (orig_test_path is not None):
            self.fill_missing_from_orig(orig_test_path)
        if not self.is_test:
            self.reduce_train_to_test_models(test_brands, test_models)
            self._process_price()
        self.dataframe['offer_id'] = self.dataframe['offer_id'].astype(str)
        self._process_mileage()
        self._reduce_photos_count(50)
        self._fix_fuel_type()
        if self.is_test and ('price' in self.dataframe.columns):
            self.dataframe.drop(columns = ['price'])
        if self.is_test and ('log_price' in self.dataframe.columns):
            self.dataframe.drop(columns = ['log_price'])
        return self.dataframe

    def prepare_frame_with_dummies(self, dummy_cols, missing_complectations=[]):
        dummies = self._generate_dummies(dummy_cols)
        complectations = self._generate_complectation_dummies()
        result = self.dataframe.drop(
            columns=dummy_cols + ['complectation']).join(dummies).join(complectations)
        if missing_complectations:
            result[missing_complectations] = 0
        return result

    @classmethod
    def equalize_columns(cls, frame_one, frame_two):
        add_to_one = set(frame_two.columns) - \
            set(frame_one.columns) - {'price'}
        add_to_two = set(frame_one.columns) - \
            set(frame_two.columns) - {'price'}
        frame_one[list(add_to_one)] = 0
        frame_two[list(add_to_two)] = 0
        return frame_one, frame_two


def numeric_plots(frame, column):
    with sns.axes_style("white"):
        fig = plt.figure(figsize=(12, 5))
        gs = fig.add_gridspec(1, 2)
        ax1 = fig.add_subplot(gs[0, 0])
        sns.histplot(data=frame, x=frame[column], hue='test', ax=ax1, bins=20)
        ax2 = fig.add_subplot(gs[0, 1])
        sns.boxplot(x=frame.test, y=frame[column] if column != 'date_posted'
                    else frame[column].apply(lambda x: x.timestamp()), ax=ax2)
        fig.tight_layout()

# %%
