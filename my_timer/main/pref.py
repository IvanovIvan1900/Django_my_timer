
class Pref:
    dic_of_pref = {'client_count_item_on_page':2}
    
    @classmethod
    def get_pref_by_name(cls, pref_name, default_value):
        """Возвращает настройку по имени.

        Args:
            pref_name ([type]): Имя настройки ('client_count_item_on_page', )
            default_value ([type]): Значение по умолчанию

        Returns:
            [type]: значение настройки
        """        
        return cls.dic_of_pref.get(pref_name,default_value)