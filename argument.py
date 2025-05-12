import argparse
import sys
from typing import Callable, Namespace, Any

class ArgumentParser(argparse.ArgumentParser):
    """Обертка на argparse с добавлением автоматической валидации."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._validators = {}

    def add_argument(
        self,
        *args,
        validator: Callable[[str], Any] = None, 
        **kwargs
    ):
        """
        Функция для добавки своей кода для проверки и приведения аргумента к конечной форме.
        
        Аргументы:
            validator: функция для проверки/преобразования аргумента.
                        Принимает единственным аргументом str возвращает Any.

        """
        argument = super().add_argument(*args, **kwargs)

        if validator is not None:
            if not callable(validator):
                raise TypeError(f"{validator.__name__} not callable")
            self._validators[argument.dest] = validator

        return argument
     
    def parse_args(self) -> Namespace:
        """
        Обертка над argparse. Принимает те же значения что и оригинал, возвращает Namespace с именованными полями.
        Значения в полях модифицированы валидаторами.
        """
        try:
            parsed_args = super().parse_args() 
        except Exception as e:
            print(f"Argument parsing error: \n{e}")
            sys.exit(1)

        for arg_name, validator in self._validators.items(): 

            arg_value = getattr(parsed_args, arg_name)

            try:
                validated_value = validator(arg_value)
                setattr(parsed_args, arg_name, validated_value)
            except Exception as e:
                print(f"Invalid value for '{arg_name}': {e}")
                sys.exit(1)
        
        return parsed_args
            
        