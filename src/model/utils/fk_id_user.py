
class AnexarFkUser():
    @staticmethod
    def anexar_fk_user(data_dict, fk_id_user):
        if not isinstance(fk_id_user, int):
            raise ValueError(f'Fk_id_user deve ser inteiro válido')
        # if not data_dict:
        #     return {**data_dict, "fk_id_user": fk_id_user}
        
        return {**data_dict, "fk_id_user": fk_id_user}
        