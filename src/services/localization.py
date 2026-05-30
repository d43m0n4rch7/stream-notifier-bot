"""Localization module parsing local YAML language definitions dynamically using static handles."""

# pyright: reportUnknownMemberType=false, reportAttributeAccessIssue=false

from pathlib import Path
from typing import Any, NewType, cast

# noinspection PyPackageRequirements
import i18n

Locale = NewType("Locale", str)
LocalizedStr = NewType("LocalizedStr", str)

__all__ = ("LocalizationManager",)


class LocalizationManager:
    """Core translation interface management component parsing international translation matrices."""

    def __init__(self, path: Path | str, default_locale: str = "ru") -> None:
        """
        Register specific directory tracks containing language dictionary file allocations.

        Parameters
        ----------
        path : Path | str
            File directory tree containing matching localization definitions.
        default_locale : str, optional
            Default fallback linguistic profile designation handle, by default "ru".
        """
        self.path = Path(path)

        i18n.load_path.append(str(self.path))
        i18n.set(key="fallback", value=default_locale)
        i18n.set(key="file_format", value="yml")
        i18n.set(key="filename_format", value="{locale}.{format}")
        i18n.set(key="skip_locale_root_data", value=True)

    @staticmethod
    def t(key: str, locale: Locale | str = "ru", **kwargs: Any) -> LocalizedStr:
        """
        Extract explicit text templates mapping context fields into corresponding structured phrases.

        Parameters
        ----------
        key : str
            Target key identifier pathway separating node sections.
        locale : Locale | str, optional
            Target language layout indicator identifier mapping, by default "ru".

        Returns
        -------
        LocalizedStr
            The processed and evaluated target translation sequence.
        """
        return LocalizedStr(cast("str", i18n.t(key, locale=str(locale), **kwargs)))
