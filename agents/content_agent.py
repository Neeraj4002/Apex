from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage
from typing import Dict, List
import json
# from json import JSONDecoder # Not strictly needed if using json.loads and string manipulation
import re # Added for _clean_json_string

class ContentAgent:
    """Agent specialized in creating engaging, platform-specific content"""

    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash-lite"): # Assuming a valid model
        self.llm = ChatGoogleGenerativeAI(
            google_api_key=api_key,
            model=model_name,
            temperature=0.7,
            max_output_tokens=2048
        )

        self.content_templates = {
            "LinkedIn Post": {
                "max_length": 500,
                "style": "Professional, thought-provoking, industry-focused",
                "elements": "Hook, insights, call-to-action, hashtags"
            },
            "Instagram Post": {
                "max_length": 300,
                "style": "Visual, engaging, lifestyle-oriented",
                "elements": "Captivating caption, emojis, hashtags, story elements"
            },
            "Newsletter": {
                "max_length": 5000,
                "style": "Informative, valuable, personal",
                "elements": "Subject line, intro, main content, conclusion, CTA"
            },
            "Blog Post": {
                "max_length": 3000,
                "style": "SEO-optimized, comprehensive, authoritative",
                "elements": "Title, introduction, headers, conclusion, meta description"
            },
            "Twitter Thread": {
                "max_length": 280, # Per tweet
                "style": "Concise, engaging, thread-worthy",
                "elements": "Hook tweet, supporting tweets, conclusion tweet"
            }
        }

    def generate_content(self, title: str, topic: str, target_audience: str,
                        content_format: str, tone: str, key_points: List[str] = None) -> Dict:
        """Generate engaging content for the specified format"""

        template_info = self.content_templates.get(content_format, self.content_templates["Blog Post"])

        content_prompt_template = PromptTemplate(
            input_variables=["title", "topic", "target_audience", "content_format", "tone", "key_points", "template_info"],
            template="""
            You are an expert content creator and copywriter. Create compelling, engaging content that forces readers to keep reading.

            Title: {title}
            Topic: {topic}
            Target Audience: {target_audience}
            Content Format: {content_format}
            Tone: {tone}
            Key Points to Include: {key_points}

            Platform Guidelines:
            - Max Length: {template_info[max_length]} characters
            - Style: {template_info[style]}
            - Required Elements: {template_info[elements]}

            Content Requirements:
            1. Start with a powerful hook that grabs attention immediately
            2. Use storytelling techniques and emotional triggers
            3. Include specific, actionable insights
            4. Avoid generic advice - be unique and memorable
            5. Use conversational language that resonates with the audience
            6. Include relevant statistics, examples, or case studies
            7. End with a strong call-to-action
            8. Optimize for the specific platform's best practices
            9. Make it scannable with proper formatting
            10. Include engagement elements (questions, polls, etc.)

            Additional Platform-Specific Requirements:
            - LinkedIn: Include industry insights, professional development angle
            - Instagram: Use emojis, visual language, lifestyle connection
            - Newsletter: Personal touch, exclusive insights, subscriber value
            - Blog: SEO optimization, comprehensive coverage, authoritative tone
            - Twitter: Viral potential, conversation starters, thread structure

            Format your response STRICTLY as a single JSON object:
            {{
                "content": "Your complete content here",
                "hashtags": ["relevant", "hashtags", "here"],
                "engagement_score": 8,
                "platform_optimization": "How this content is optimized for the platform",
                "cta": "Your call-to-action",
                "estimated_reach": "Potential reach estimate"
            }}
            Ensure the output is ONLY the JSON object, with no surrounding text or explanations.
            """
        )

        raw_llm_response_content = "" # Initialize for logging in case of early error
        try:
            key_points_str = ", ".join(key_points) if key_points else "None specified"

            prompt = content_prompt_template.format(
                title=title,
                topic=topic,
                target_audience=target_audience,
                content_format=content_format,
                tone=tone,
                key_points=key_points_str,
                template_info=template_info
            )

            response = self.llm.invoke([HumanMessage(content=prompt)])
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
                    print(f"Warning: LLM response in generate_content does not appear to contain a JSON object. Response: {raw_llm_response_content}")
                    # Fall through to parsing attempt, which will likely fail and use fallback

            try:
                cleaned_json_str = self._clean_json_string(content_str)
                parsed_output = json.loads(cleaned_json_str)
                return parsed_output
            except json.JSONDecodeError as json_e:
                print(f"Error decoding JSON in generate_content: {json_e}. Cleaned string was: '{cleaned_json_str}'. Original LLM response: '{raw_llm_response_content}'")
                return {
                    "content": raw_llm_response_content,
                    "hashtags": self._extract_hashtags(raw_llm_response_content),
                    "engagement_score": 5,
                    "platform_optimization": f"Failed to parse structured output for {content_format}. Raw LLM output provided.",
                    "cta": "Review content manually.",
                    "estimated_reach": "Unknown (parsing error)"
                }

        except Exception as e:
            print(f"Error generating content: {e}. Original LLM response might have been: '{raw_llm_response_content}'")
            return self._get_default_content(title, topic, content_format)

    def optimize_for_platform(self, content: str, platform: str) -> Dict:
        """Optimize existing content for a specific platform"""
        optimization_prompt_str = f"""
        You are an expert content optimizer. Optimize the following content for {platform}.

        Content to optimize:
        ---
        {content}
        ---

        Platform-specific optimizations needed:
        - Adjust length and format to suit {platform}.
        - Add platform-specific elements (e.g., hashtags, emojis, mentions if appropriate for {platform}).
        - Enhance engagement potential for {platform}'s audience.
        - Include relevant keywords if applicable.

        Format your response STRICTLY as a single JSON object with the following keys:
        - "optimized_content": (string) The full optimized content.
        - "explanation_of_changes": (string) A summary of the changes made and why.
        - "original_length": {len(content)},
        - "optimized_length": (integer) Character count of the optimized content.
        - "platform_elements_summary": (string) Brief summary of platform-specific elements added/adjusted.

        Example JSON output:
        {{
            "optimized_content": "Your newly optimized content for {platform}...",
            "explanation_of_changes": "Shortened the content. Added relevant hashtags for {platform}. Rephrased the CTA.",
            "original_length": {len(content)},
            "optimized_length": 150,
            "platform_elements_summary": "Added 3 hashtags, 2 emojis. Adjusted for brevity."
        }}
        Ensure the output is ONLY the JSON object, with no surrounding text or explanations.
        """
        raw_llm_response_content = ""
        try:
            response = self.llm.invoke([HumanMessage(content=optimization_prompt_str)])
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
                    print(f"Warning: LLM response in optimize_for_platform does not appear to be a JSON object. Response: {raw_llm_response_content}")

            try:
                cleaned_json_str = self._clean_json_string(content_str)
                parsed_output = json.loads(cleaned_json_str)
                if "original_length" not in parsed_output: # Add if LLM missed it
                    parsed_output["original_length"] = len(content)
                return parsed_output
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON in optimize_for_platform: {e}. Cleaned string: '{content_str}'. Original: '{raw_llm_response_content}'")
                return {"error": f"JSONDecodeError: {e}", "raw_response": raw_llm_response_content}
        except Exception as e:
            print(f"Error in optimize_for_platform: {e}. Original LLM response: '{raw_llm_response_content}'")
            return {"error": str(e), "raw_response": raw_llm_response_content}


    def _extract_hashtags(self, content: str) -> List[str]:
        """Extract hashtags from content"""
        words = content.split()
        hashtags = [word for word in words if word.startswith('#')]
        return hashtags[:10]

    def _get_default_content(self, title: str, topic: str, content_format: str) -> Dict:
        """Default content as fallback"""
        return {
            "content": f"Exploring {topic}: {title}\n\nThis is an engaging piece about {topic} that provides valuable insights for our audience. Stay tuned for more updates!",
            "hashtags": ["#content", "#strategy", "#marketing"],
            "engagement_score": 6,
            "platform_optimization": f"Basic optimization for {content_format} (default fallback content).",
            "cta": "What are your thoughts on this topic?",
            "estimated_reach": "Moderate reach potential (default fallback content)."
        }

    def analyze_content_performance(self, content_to_analyze: str) -> Dict:
        """Analyze content for engagement and performance potential"""
        analysis_prompt_str = f"""
        Analyze this content for engagement and performance potential:
        ---
        {content_to_analyze}
        ---

        Provide analysis on:
        1. Engagement score (1-10)
        2. Readability score (1-10, e.g., Flesch-Kincaid)
        3. Emotional impact (1-10, considering sentiment and tone)
        4. Call-to-action effectiveness (1-10)
        5. Platform optimization (1-10, general assessment if platform not specified)
        6. Specific improvement suggestions (actionable, concrete list)

        Format your response STRICTLY as a single JSON object with keys: "engagement_score", "readability_score", "emotional_impact", "cta_effectiveness", "platform_optimization_score", "improvement_suggestions" (a list of strings).
        Example:
        {{
            "engagement_score": 7,
            "readability_score": 8,
            "emotional_impact": 6,
            "cta_effectiveness": 7,
            "platform_optimization_score": 8,
            "improvement_suggestions": ["Make the hook more compelling by...", "Consider adding a specific example to illustrate point X."]
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
                     print(f"Warning: LLM response in analyze_content_performance does not appear to be a JSON object. Response: {raw_llm_response_content}")

            try:
                cleaned_json_str = self._clean_json_string(content_str)
                parsed_output = json.loads(cleaned_json_str)
                return {"analysis": parsed_output}
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON in analyze_content_performance: {e}. Cleaned string: '{content_str}'. Original: '{raw_llm_response_content}'")
                return {"error": f"JSONDecodeError: {e}", "raw_response": raw_llm_response_content}
        except Exception as e:
            print(f"Error in analyze_content_performance: {e}. Original LLM response: '{raw_llm_response_content}'")
            return {"error": str(e), "raw_response": raw_llm_response_content}

    def _clean_json_string(self, json_str: str) -> str:
        """Clean and fix common JSON formatting issues"""
        # Remove any trailing commas before closing brackets/braces
        json_str = json_str.replace(',]', ']').replace(',}', '}')
        
        # Ensure property names (keys) are in double quotes
        # This regex is a bit simple and might fail on complex keys, but good for typical identifiers
        json_str = re.sub(r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', json_str)
        
        # Attempt to fix single quotes used for string values IF they are at the start/end of a value
        # This is heuristic and can be risky if single quotes are meant to be part of the string.
        # A more robust solution would involve a proper tokenizer or more complex regex.
        # For now, keep the original broad replacement, but be aware of its limitations.
        # json_str = json_str.replace("'", '"') # This is too broad and can break legitimate apostrophes.
                                            # LLM should be instructed to use double quotes.
                                            # If needed, more complex regex could be:
                                            # re.sub(r":\s*'(.*?)'", r': "\1"', json_str) but this is still limited.
                                            # For now, rely on LLM producing double quotes or simple key cleaning.
        return json_str

# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain.prompts import PromptTemplate
# from langchain.schema import HumanMessage
# from typing import Dict, List
# import json
# from json import JSONDecoder

# class ContentAgent:
#     """Agent specialized in creating engaging, platform-specific content"""
    
#     def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash-lite"):
#         self.llm = ChatGoogleGenerativeAI(
#             google_api_key=api_key,
#             model=model_name,
#             temperature=0.7,
#             max_output_tokens=2048
#         )
        
#         self.content_templates = {
#             "LinkedIn Post": {
#                 "max_length": 500,
#                 "style": "Professional, thought-provoking, industry-focused",
#                 "elements": "Hook, insights, call-to-action, hashtags"
#             },
#             "Instagram Post": {
#                 "max_length": 300,
#                 "style": "Visual, engaging, lifestyle-oriented",
#                 "elements": "Captivating caption, emojis, hashtags, story elements"
#             },
#             "Newsletter": {
#                 "max_length": 5000,
#                 "style": "Informative, valuable, personal",
#                 "elements": "Subject line, intro, main content, conclusion, CTA"
#             },
#             "Blog Post": {
#                 "max_length": 3000,
#                 "style": "SEO-optimized, comprehensive, authoritative",
#                 "elements": "Title, introduction, headers, conclusion, meta description"
#             },
#             "Twitter Thread": {
#                 "max_length": 280,
#                 "style": "Concise, engaging, thread-worthy",
#                 "elements": "Hook tweet, supporting tweets, conclusion tweet"
#             }
#         }
    
#     def generate_content(self, title: str, topic: str, target_audience: str, 
#                         content_format: str, tone: str, key_points: List[str] = None) -> Dict:
#         """Generate engaging content for the specified format"""
        
#         template_info = self.content_templates.get(content_format, self.content_templates["Blog Post"])
        
#         content_prompt = PromptTemplate(
#             input_variables=["title", "topic", "target_audience", "content_format", "tone", "key_points", "template_info"],
#             template="""
#             You are an expert content creator and copywriter. Create compelling, engaging content that forces readers to keep reading.
            
#             Title: {title}
#             Topic: {topic}
#             Target Audience: {target_audience}
#             Content Format: {content_format}
#             Tone: {tone}
#             Key Points to Include: {key_points}
            
#             Platform Guidelines:
#             - Max Length: {template_info[max_length]} characters
#             - Style: {template_info[style]}
#             - Required Elements: {template_info[elements]}
            
#             Content Requirements:
#             1. Start with a powerful hook that grabs attention immediately
#             2. Use storytelling techniques and emotional triggers
#             3. Include specific, actionable insights
#             4. Avoid generic advice - be unique and memorable
#             5. Use conversational language that resonates with the audience
#             6. Include relevant statistics, examples, or case studies
#             7. End with a strong call-to-action
#             8. Optimize for the specific platform's best practices
#             9. Make it scannable with proper formatting
#             10. Include engagement elements (questions, polls, etc.)
            
#             Additional Platform-Specific Requirements:
#             - LinkedIn: Include industry insights, professional development angle
#             - Instagram: Use emojis, visual language, lifestyle connection
#             - Newsletter: Personal touch, exclusive insights, subscriber value
#             - Blog: SEO optimization, comprehensive coverage, authoritative tone
#             - Twitter: Viral potential, conversation starters, thread structure
            
#             Format your response as JSON:
#             {
#                 "content": "Your complete content here",
#                 "hashtags": ["relevant", "hashtags", "here"],
#                 "engagement_score": 8,
#                 "platform_optimization": "How this content is optimized for the platform",
#                 "cta": "Your call-to-action",
#                 "estimated_reach": "Potential reach estimate"
#             }
#             """
#         )
#         from json import JSONDecoder
#         #try:
#         key_points_str = ", ".join(key_points) if key_points else "None specified"
        
#         prompt = content_prompt.format(
#             title=title,
#             topic=topic,
#             target_audience=target_audience,
#             content_format=content_format,
#             tone=tone,
#             key_points=key_points_str,
#             template_info=template_info
#         )
        
#         response = self.llm.invoke([HumanMessage(content=prompt)])
#         return response.content
        
#             # Extract JSON from response
#             # Try to decode the first valid JSON object using JSONDecoder
#         #     decoder = JSONDecoder()
#         #     try:
#         #         result, _ = decoder.raw_decode(content)
#         #         return result
#         #     except Exception:
#         #         # Fallback to old method if decoding fails
#         #         start_idx = content.find('{')
#         #         end_idx = content.rfind('}') + 1
#         #         if start_idx != -1 and end_idx != -1:
#         #             json_str = content[start_idx:end_idx].strip()
#         #             cleaned_json = self._clean_json_string(json_str)
#         #             return json.loads(cleaned_json)
#         #         else:
#         #             return {
#         #                 "content": content,
#         #                 "hashtags": self._extract_hashtags(content),
#         #                 "engagement_score": 7,
#         #                 "platform_optimization": f"Content optimized for {content_format}",
#         #                 "cta": "Engage with this content!",
#         #                 "estimated_reach": "Medium reach potential"
#         #             }

#         # except Exception as e:
#         #     print(f"Error generating content: {e}")
#         #     return self._get_default_content(title, topic, content_format)
    
#     def optimize_for_platform(self, content: str, platform: str) -> Dict:
#         """Optimize existing content for a specific platform"""
        
#         optimization_prompt = f"""
#         Optimize this content for {platform}:
        
#         {content}
        
#         Platform-specific optimizations needed:
#         - Adjust length and format
#         - Add platform-specific elements
#         - Optimize engagement potential
#         - Include relevant hashtags/keywords
        
#         Return optimized content with explanation of changes made.
#         """
        
#         try:
#             response = self.llm.invoke([HumanMessage(content=optimization_prompt)])
#             return {"optimized_content": response.content}
#         except Exception as e:
#             return {"error": str(e)}
    
#     def _extract_hashtags(self, content: str) -> List[str]:
#         """Extract hashtags from content"""
#         words = content.split()
#         hashtags = [word for word in words if word.startswith('#')]
#         return hashtags[:10]  # Return max 10 hashtags
    
#     def _get_default_content(self, title: str, topic: str, content_format: str) -> Dict:
#         """Default content as fallback"""
#         return {
#             "content": f"Exploring {topic}: {title}\n\nThis is an engaging piece about {topic} that provides valuable insights for our audience. Stay tuned for more updates!",
#             "hashtags": ["#content", "#strategy", "#marketing"],
#             "engagement_score": 6,
#             "platform_optimization": f"Basic optimization for {content_format}",
#             "cta": "What are your thoughts on this topic?",
#             "estimated_reach": "Moderate reach potential"
#         }
    
#     def analyze_content_performance(self, content: str) -> Dict:
#         """Analyze content for engagement and performance potential"""
        
#         analysis_prompt = f"""
#         Analyze this content for engagement and performance potential:
        
#         {content}
        
#         Provide analysis on:
#         1. Engagement score (1-10)
#         2. Readability score (1-10)
#         3. Emotional impact (1-10)
#         4. Call-to-action effectiveness (1-10)
#         5. Platform optimization (1-10)
#         6. Specific improvement suggestions
        
#         Format as detailed analysis.
#         """
        
#         try:
#             response = self.llm.invoke([HumanMessage(content=analysis_prompt)])
#             return {"analysis": response.content}
#         except Exception as e:
#             return {"error": str(e)}
    
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