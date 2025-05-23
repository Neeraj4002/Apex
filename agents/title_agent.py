from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage
from typing import List, Dict
import json
import re # Added for _clean_json_string

class TitleAgent:
    """Agent specialized in generating SEO-optimized and trendy titles"""

    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash-lite"): # Assuming a valid model
        self.llm = ChatGoogleGenerativeAI(
            google_api_key=api_key,
            model=model_name,
            temperature=0.8,
            max_output_tokens=1024
        )

        self.title_prompt_template = PromptTemplate(
            input_variables=["topic", "target_audience", "content_format", "tone"],
            template="""
            You are an expert content strategist and SEO specialist. Generate 5 compelling, SEO-optimized titles for the following:

            Topic: {topic}
            Target Audience: {target_audience}
            Content Format: {content_format}
            Tone: {tone}

            Requirements:
            1. Each title should be attention-grabbing and click-worthy
            2. Include relevant keywords for SEO
            3. Use power words and emotional triggers
            4. Keep titles between 50-60 characters for optimal SEO (strict adherence if possible, else note deviation)
            5. Make them specific and actionable
            6. Avoid generic or cliché phrases
            7. Consider current trends and viral content patterns

            Format your response STRICTLY as a single JSON array of objects, where each object contains 'title', 'seo_score' (integer 1-10), and 'reasoning' (string).
            Example:
            [
                {{
                    "title": "Your Compelling Title Here: Boost Engagement Now!",
                    "seo_score": 9,
                    "reasoning": "Uses strong keywords, actionable language, and a colon for clarity. Length is optimal."
                }},
                {{
                    "title": "Unlock the Secrets of {topic} for {target_audience}",
                    "seo_score": 8,
                    "reasoning": "Appeals to curiosity and specifies target audience. Includes topic keyword."
                }}
            ]
            Ensure the output is ONLY the JSON array, with no surrounding text or explanations.
            """
        )

    def generate_titles(self, topic: str, target_audience: str, content_format: str, tone: str) -> List[Dict]:
        """Generate SEO-optimized titles for the given parameters"""
        raw_llm_response_content = ""
        try:
            prompt = self.title_prompt_template.format(
                topic=topic,
                target_audience=target_audience,
                content_format=content_format,
                tone=tone
            )

            response = self.llm.invoke([HumanMessage(content=prompt)])
            raw_llm_response_content = response.content
            content_str = raw_llm_response_content.strip()
            
            if content_str.startswith("```json"):
                content_str = content_str[7:]
                if content_str.endswith("```"):
                    content_str = content_str[:-3]
                content_str = content_str.strip()
            elif not (content_str.startswith("[") and content_str.endswith("]")):
                start_idx = content_str.find('[')
                end_idx = content_str.rfind(']') + 1
                if start_idx != -1 and end_idx != -1:
                    content_str = content_str[start_idx:end_idx]
                else:
                    print(f"Warning: LLM response in generate_titles does not appear to be a JSON array. Response: {raw_llm_response_content}")

            try:
                cleaned_json_str = self._clean_json_string(content_str)
                parsed_output = json.loads(cleaned_json_str)
                if isinstance(parsed_output, list):
                    return parsed_output
                else:
                    print(f"Error: Parsed output in generate_titles is not a list. Output: {parsed_output}")
                    return self._get_default_titles(topic) # Fallback if not a list
            except json.JSONDecodeError as json_e:
                print(f"Error decoding JSON in generate_titles: {json_e}. Cleaned string: '{cleaned_json_str}'. Original: '{raw_llm_response_content}'")
                # Fallback to trying to parse manually from the raw response
                fallback_titles = self._parse_fallback_titles(raw_llm_response_content)
                if fallback_titles:
                    return fallback_titles
                return self._get_default_titles(topic)

        except Exception as e:
            print(f"Error generating titles: {e}. Original LLM response: '{raw_llm_response_content}'")
            return self._get_default_titles(topic)

    def _clean_json_string(self, json_str: str) -> str:
        """Clean and fix common JSON formatting issues"""
        json_str = json_str.replace(',]', ']').replace(',}', '}')
        json_str = re.sub(r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', json_str)
        # Avoid broad replace of single to double quotes as it breaks apostrophes.
        # Rely on LLM for correct quoting or more advanced cleaning if necessary.
        return json_str

    def _parse_fallback_titles(self, content: str) -> List[Dict]:
        """Fallback method to parse titles if JSON parsing fails"""
        lines = content.split('\n')
        titles = []
        current_title_data = {}

        for line in lines:
            line_strip = line.strip()
            if '"title":' in line_strip:
                if current_title_data: # Save previous if any
                    if "title" in current_title_data and "seo_score" in current_title_data and "reasoning" in current_title_data:
                        titles.append(current_title_data)
                current_title_data = {}
                try:
                    current_title_data["title"] = line_strip.split('"title":')[1].split(',')[0].replace('"', '').strip()
                except IndexError: pass
            elif '"seo_score":' in line_strip and current_title_data:
                try:
                    score_str = line_strip.split('"seo_score":')[1].split(',')[0].strip()
                    current_title_data["seo_score"] = int(score_str)
                except (IndexError, ValueError):
                    current_title_data["seo_score"] = 7 # default
            elif '"reasoning":' in line_strip and current_title_data:
                try:
                    current_title_data["reasoning"] = line_strip.split('"reasoning":')[1].replace('"', '').replace('}', '').strip()
                except IndexError: pass
        
        if current_title_data and "title" in current_title_data and "seo_score" in current_title_data and "reasoning" in current_title_data: # Add last one
             titles.append(current_title_data)

        if not titles: # Simpler fallback if above fails
            for line in content.splitlines():
                 if line.strip().startswith("Title:") or line.strip().startswith('"title":'):
                     title_text = line.split(":", 1)[-1].strip().replace('"',"").replace(',','')
                     if 10 < len(title_text) < 100: # Basic sanity check
                        titles.append({
                            "title": title_text,
                            "seo_score": 7,
                            "reasoning": "Fallback parsed title with good potential"
                        })
        return titles[:5]

    def _get_default_titles(self, topic: str) -> List[Dict]:
        """Default titles as fallback"""
        return [
            {
                "title": f"The Ultimate Guide to {topic}",
                "seo_score": 8,
                "reasoning": "Ultimate guides perform well in search results (default fallback)"
            },
            {
                "title": f"5 Proven Strategies for {topic} Success",
                "seo_score": 7,
                "reasoning": "Number-based titles attract clicks (default fallback)"
            }
        ]

    def analyze_title_performance(self, title_to_analyze: str) -> Dict:
        """Analyze a title's potential performance"""
        analysis_prompt_str = f"""
        Analyze this title for SEO and engagement potential: "{title_to_analyze}"

        Provide analysis on:
        1. SEO score (1-10) based on keyword presence, relevance, and structure.
        2. Click-through rate (CTR) potential (1-10) considering appeal and clarity.
        3. Emotional impact (1-10) (e.g., curiosity, urgency, excitement).
        4. Keyword optimization (briefly state how well keywords are used or could be improved).
        5. Suggestions for improvement (actionable, specific list of strings).

        Format your response STRICTLY as a single JSON object with these fields: "seo_score", "ctr_potential", "emotional_impact", "keyword_optimization", "improvement_suggestions" (list of strings).
        Example:
        {{
            "seo_score": 8,
            "ctr_potential": 7,
            "emotional_impact": 6,
            "keyword_optimization": "Keywords '{title_to_analyze.split()[0] if title_to_analyze else 'example'}' are present. Consider adding a secondary keyword.",
            "improvement_suggestions": ["Could be more specific to the benefit.", "Test a version with a number."]
        }}
        Ensure the output is ONLY the JSON object, with no surrounding text or explanations.
        """
        raw_llm_response_content = ""
        try:
            response = self.llm.invoke([HumanMessage(content=analysis_prompt_str)])
            raw_llm_response_content = response.content
            content_str = raw_llm_response_content.strip()

            if content_str.startswith("```json"):
                content_str = content_str[7:]
                if content_str.endswith("```"):
                    content_str = content_str[:-3]
                content_str = content_str.strip()
            elif not (content_str.startswith("{") and content_str.endswith("}")):
                start_idx = content_str.find('{')
                end_idx = content_str.rfind('}') + 1
                if start_idx != -1 and end_idx != -1:
                    content_str = content_str[start_idx:end_idx]
                else:
                    print(f"Warning: LLM response in analyze_title_performance does not appear to be a JSON object. Response: {raw_llm_response_content}")

            try:
                cleaned_json_str = self._clean_json_string(content_str)
                parsed_output = json.loads(cleaned_json_str)
                return {"analysis": parsed_output}
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON in analyze_title_performance: {e}. Cleaned string: '{content_str}'. Original: '{raw_llm_response_content}'")
                return {"error": f"JSONDecodeError: {e}", "raw_response": raw_llm_response_content}
        except Exception as e:
            print(f"Error in analyze_title_performance: {e}. Original LLM response: '{raw_llm_response_content}'")
            return {"error": str(e), "raw_response": raw_llm_response_content}

# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain.prompts import PromptTemplate
# from langchain.schema import HumanMessage
# from typing import List, Dict
# import json

# class TitleAgent:
#     """Agent specialized in generating SEO-optimized and trendy titles"""
    
#     def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash-lite"):
#         self.llm = ChatGoogleGenerativeAI(
#             google_api_key=api_key,
#             model=model_name,
#             temperature=0.8,
#             max_output_tokens=1024
#         )
        
#         self.title_prompt = PromptTemplate(
#             input_variables=["topic", "target_audience", "content_format", "tone"],
#             template="""
#             You are an expert content strategist and SEO specialist. Generate 5 compelling, SEO-optimized titles for the following:
            
#             Topic: {topic}
#             Target Audience: {target_audience}
#             Content Format: {content_format}
#             Tone: {tone}
            
#             Requirements:
#             1. Each title should be attention-grabbing and click-worthy
#             2. Include relevant keywords for SEO
#             3. Use power words and emotional triggers
#             4. Keep titles between 50-60 characters for optimal SEO
#             5. Make them specific and actionable
#             6. Avoid generic or cliché phrases
#             7. Consider current trends and viral content patterns
            
#             Format your response as a JSON array with objects containing 'title', 'seo_score' (1-10), and 'reasoning':
            
#             [
#                 {
#                     "title": "Your compelling title here",
#                     "seo_score": 9,
#                     "reasoning": "Why this title works well"
#                 }
#             ]
#             """
#         )
    
#     def generate_titles(self, topic: str, target_audience: str, content_format: str, tone: str) -> List[Dict]:
#         """Generate SEO-optimized titles for the given parameters"""
#         try:
#             prompt = self.title_prompt.format(
#                 topic=topic,
#                 target_audience=target_audience,
#                 content_format=content_format,
#                 tone=tone
#             )
            
#             response = self.llm.invoke([HumanMessage(content=prompt)])
            
#             # Extract JSON from response
#             return  response.content
            
#             # Find JSON array in the response
#              # Try to decode the first valid JSON array using JSONDecoder
#             # decoder = JSONDecoder()
#             # try:
#             #     titles, _ = decoder.raw_decode(content)
#             #     return titles
#             # except Exception:
#             #     # Fallback to old slicing if decoding fails
#             #     start_idx = content.find('[')
#             #     end_idx = content.rfind(']') + 1
#             #     if start_idx != -1 and end_idx != -1:
#             #         json_str = content[start_idx:end_idx].strip()
#             #         cleaned_json = self._clean_json_string(json_str)
#             #         return json.loads(cleaned_json)
#             #     else:
#             #         # Fallback: parse manually if nothing works
#             #         return self._parse_fallback_titles(content)
   
#         except Exception as e:
#             print(f"Error generating titles: {e}")
#             return self._get_default_titles(topic)
    
#     def _clean_json_string(self, json_str: str) -> str:
#         """Clean and fix common JSON formatting issues"""
#         # Remove any trailing commas before closing brackets
#         json_str = json_str.replace(',]', ']').replace(',}', '}')
        
#         # Ensure property names are in double quotes
#         import re
#         json_str = re.sub(r'([{,]\s*)([\w]+)\s*:', r'\1"\2":', json_str)
        
#         # Fix any single quotes used instead of double quotes
#         json_str = json_str.replace("'", '"')
        
#         return json_str
    
#     def _parse_fallback_titles(self, content: str) -> List[Dict]:
#         """Fallback method to parse titles if JSON parsing fails"""
#         lines = content.split('\n')
#         titles = []
        
#         for line in lines:
#             if line.strip() and not line.startswith(('You are', 'Topic:', 'Requirements:', 'Format')):
#                 if len(line.strip()) > 10:  # Reasonable title length
#                     titles.append({
#                         "title": line.strip().replace('"', '').replace('-', '').strip(),
#                         "seo_score": 7,
#                         "reasoning": "Generated title with good potential"
#                     })
                    
#         return titles[:5]  # Return max 5 titles
    
#     def _get_default_titles(self, topic: str) -> List[Dict]:
#         """Default titles as fallback"""
#         return [
#             {
#                 "title": f"The Ultimate Guide to {topic}",
#                 "seo_score": 8,
#                 "reasoning": "Ultimate guides perform well in search results"
#             },
#             {
#                 "title": f"5 Proven Strategies for {topic} Success",
#                 "seo_score": 7,
#                 "reasoning": "Number-based titles attract clicks"
#             },
#             {
#                 "title": f"Why {topic} is Changing Everything in 2024",
#                 "seo_score": 8,
#                 "reasoning": "Trend-based titles with current year"
#             }
#         ]
    
#     def analyze_title_performance(self, title: str) -> Dict:
#         """Analyze a title's potential performance"""
#         analysis_prompt = f"""
#         Analyze this title for SEO and engagement potential: "{title}"
        
#         Provide analysis on:
#         1. SEO score (1-10)
#         2. Click-through rate potential (1-10)
#         3. Emotional impact (1-10)
#         4. Keyword optimization
#         5. Suggestions for improvement
        
#         Format as JSON with these fields.
#         """
        
#         try:
#             response = self.llm.invoke([HumanMessage(content=analysis_prompt)])
#             # Parse and return analysis
#             return {"analysis": response.content}
#         except Exception as e:
#             return {"error": str(e)}