"""Selector validation service"""

import logging
import re
from typing import Optional, Tuple

from lxml import etree
from cssselect import GenericTranslator, SelectorError

from app.exceptions import ValidationError

logger = logging.getLogger(__name__)


class SelectorValidator:
    """Service for validating CSS and XPath selectors"""

    @staticmethod
    def validate_css_selector(selector: str) -> Tuple[bool, Optional[str]]:
        """
        Validate CSS selector syntax.
        
        Args:
            selector: CSS selector string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not selector or not selector.strip():
            return False, "Selector cannot be empty"
        
        try:
            # Try to translate CSS to XPath
            translator = GenericTranslator()
            translator.css_to_xpath(selector)
            return True, None
        except SelectorError as e:
            logger.warning(f"Invalid CSS selector: {selector}, error: {str(e)}")
            return False, f"Invalid CSS selector: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error validating CSS selector: {str(e)}")
            return False, f"Error validating selector: {str(e)}"

    @staticmethod
    def validate_xpath_selector(selector: str) -> Tuple[bool, Optional[str]]:
        """
        Validate XPath selector syntax.
        
        Args:
            selector: XPath selector string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not selector or not selector.strip():
            return False, "Selector cannot be empty"
        
        try:
            # Try to compile XPath
            etree.XPath(selector)
            return True, None
        except etree.XPathError as e:
            logger.warning(f"Invalid XPath selector: {selector}, error: {str(e)}")
            return False, f"Invalid XPath selector: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error validating XPath selector: {str(e)}")
            return False, f"Error validating selector: {str(e)}"

    @staticmethod
    def validate_selector(selector: str, selector_type: str) -> Tuple[bool, Optional[str]]:
        """
        Validate selector based on type.
        
        Args:
            selector: Selector string
            selector_type: Type of selector ('css' or 'xpath')
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if selector_type.lower() == "css":
            return SelectorValidator.validate_css_selector(selector)
        elif selector_type.lower() == "xpath":
            return SelectorValidator.validate_xpath_selector(selector)
        else:
            return False, f"Unknown selector type: {selector_type}"

    @staticmethod
    def test_selector(html_content: str, selector: str, selector_type: str) -> Tuple[int, list]:
        """
        Test selector against HTML content.
        
        Args:
            html_content: HTML content to test against
            selector: Selector string
            selector_type: Type of selector ('css' or 'xpath')
            
        Returns:
            Tuple of (match_count, preview_data)
        """
        try:
            from lxml import html as lxml_html
            
            # Parse HTML
            tree = lxml_html.fromstring(html_content)
            
            if selector_type.lower() == "css":
                # Convert CSS to XPath
                translator = GenericTranslator()
                xpath = translator.css_to_xpath(selector)
                elements = tree.xpath(xpath)
            elif selector_type.lower() == "xpath":
                elements = tree.xpath(selector)
            else:
                return 0, []
            
            # Generate preview data (first 5 matches)
            preview_data = []
            for i, element in enumerate(elements[:5]):
                try:
                    text = element.text_content().strip()[:200]  # Limit to 200 chars
                    preview_data.append({
                        "index": i,
                        "text": text,
                        "tag": element.tag,
                    })
                except Exception as e:
                    logger.warning(f"Error extracting element text: {str(e)}")
                    preview_data.append({
                        "index": i,
                        "text": "[Unable to extract text]",
                        "tag": element.tag,
                    })
            
            return len(elements), preview_data
            
        except Exception as e:
            logger.error(f"Error testing selector: {str(e)}")
            raise ValidationError(f"Error testing selector: {str(e)}")

    @staticmethod
    def get_selector_suggestions(selector: str, selector_type: str, error_message: str) -> list:
        """
        Get suggestions for fixing invalid selector.
        
        Args:
            selector: Invalid selector string
            selector_type: Type of selector
            error_message: Error message from validation
            
        Returns:
            List of suggestions
        """
        suggestions = []
        
        if selector_type.lower() == "css":
            # CSS selector suggestions
            if "invalid" in error_message.lower():
                suggestions.append("Check for unmatched brackets or quotes")
                suggestions.append("Ensure selector follows CSS syntax rules")
            
            if "[" in selector and "]" not in selector:
                suggestions.append("Add closing bracket ] for attribute selector")
            
            if "(" in selector and ")" not in selector:
                suggestions.append("Add closing parenthesis ) for pseudo-class")
            
            if selector.startswith(" "):
                suggestions.append("Remove leading space from selector")
            
            if selector.endswith(" "):
                suggestions.append("Remove trailing space from selector")
        
        elif selector_type.lower() == "xpath":
            # XPath suggestions
            if "invalid" in error_message.lower():
                suggestions.append("Check for unmatched brackets or quotes")
                suggestions.append("Ensure XPath follows XPath syntax rules")
            
            if "[" in selector and "]" not in selector:
                suggestions.append("Add closing bracket ] for predicate")
            
            if "(" in selector and ")" not in selector:
                suggestions.append("Add closing parenthesis ) for function")
            
            if not selector.startswith("/") and not selector.startswith("."):
                suggestions.append("XPath should start with / or .")
        
        if not suggestions:
            suggestions.append("Review selector syntax and try again")
        
        return suggestions
