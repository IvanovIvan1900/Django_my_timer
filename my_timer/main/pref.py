
class Pref:
    dic_of_pref = {'client_count_item_on_page':50,
    'task_count_item_on_page':50,
    'work_place_count_last_task':20,
    }
    
    @classmethod
    def get_pref_by_name(cls, pref_name, default_value):
        """Возвращает настройку по имени.

        Args:
            pref_name ([type]): Имя настройки ('client_count_item_on_page', 'task_count_item_on_page', 'work_place_count_last_task')
            default_value ([type]): Значение по умолчанию

        Returns:
            [type]: значение настройки
        """        
        return cls.dic_of_pref.get(pref_name,default_value)