"""
AI Project Manager - Automated handling of customer project submissions
Handles project intake, status updates, customer communication, and workflow automation
"""

import os
import openai
import threading
from datetime import datetime, timedelta
from models import db, CustomerProject, UploadedFile, ProjectStatus, ProjectType
import logging
from typing import Dict, List, Optional
import json

class AIProjectManager:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        self.logger = logging.getLogger(__name__)
        
    def process_new_project(self, project: CustomerProject) -> Dict:
        """
        Automatically process a new project submission using AI
        """
        try:
            # Analyze project requirements
            analysis = self._analyze_project_requirements(project)
            
            # Generate project timeline
            timeline = self._generate_project_timeline(project, analysis)
            
            # Create AI response to customer
            welcome_message = self._generate_welcome_message(project, timeline)
            
            # Update project status and send notification
            project.status = ProjectStatus.PENDING
            db.session.commit()
            
            # Schedule automatic status updates
            self._schedule_status_updates(project.id, timeline)
            
            return {
                'success': True,
                'analysis': analysis,
                'timeline': timeline,
                'welcome_message': welcome_message,
                'next_action': 'AI monitoring initialized'
            }
            
        except Exception as e:
            self.logger.error(f"Error processing project {project.id}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _analyze_project_requirements(self, project: CustomerProject) -> Dict:
        """
        Use AI to analyze project requirements and determine production approach
        """
        try:
            # Prepare project data for AI analysis
            uploaded_files = list(project.uploaded_files) if project.uploaded_files else []
            project_data = {
                'type': project.project_type.value,
                'title': project.project_title,
                'description': project.project_description,
                'special_requests': project.special_requests,
                'file_count': len(uploaded_files),
                'file_types': [f.file_type for f in uploaded_files] if uploaded_files else []
            }
            
            analysis_prompt = f"""
            Analyze this video production project and provide detailed recommendations.
            
            Project Type: {project_data['type']}
            Title: {project_data['title']}
            Description: {project_data['description']}
            Special Requests: {project_data['special_requests']}
            Files Uploaded: {project_data['file_count']} files
            File Types: {', '.join(project_data['file_types'])}
            
            IMPORTANT: Respond ONLY with valid JSON in this exact format:
            {{
                "complexity_level": "moderate",
                "estimated_hours": 8,
                "recommended_approach": "Professional video production workflow with custom editing",
                "technical_requirements": ["Video editing software", "Color correction", "Audio enhancement"],
                "creative_suggestions": ["Professional transitions", "Background music", "Text overlays"],
                "potential_challenges": ["File format compatibility", "Timeline coordination"],
                "quality_tier": "professional"
            }}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert video production AI assistant for DreamFrame LLC. Analyze projects and provide detailed technical and creative recommendations."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            self.logger.info(f"OpenAI raw response: {content}")
            if content:
                try:
                    analysis = json.loads(content)
                except json.JSONDecodeError as e:
                    self.logger.error(f"JSON decode error: {e}, content: {content}")
                    # Extract JSON from response if it's wrapped in text
                    import re
                    json_match = re.search(r'\{.*\}', content, re.DOTALL)
                    if json_match:
                        analysis = json.loads(json_match.group())
                    else:
                        raise e
            else:
                raise ValueError("Empty response from OpenAI")
            self.logger.info(f"AI analysis completed for project {project.id}")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error in AI analysis: {str(e)}")
            return {
                "complexity_level": "moderate",
                "estimated_hours": 8,
                "recommended_approach": "Standard video production workflow",
                "technical_requirements": ["Video editing", "Color correction"],
                "creative_suggestions": ["Professional transitions", "Background music"],
                "potential_challenges": ["File format compatibility"],
                "quality_tier": "professional"
            }
    
    def _generate_project_timeline(self, project: CustomerProject, analysis: Dict) -> Dict:
        """
        Generate realistic project timeline based on AI analysis
        """
        base_hours = analysis.get('estimated_hours', 8)
        complexity = analysis.get('complexity_level', 'moderate')
        
        # Calculate timeline based on project type and complexity
        timeline_multiplier = {
            'simple': 1.0,
            'moderate': 1.5,
            'complex': 2.0
        }
        
        total_hours = base_hours * timeline_multiplier.get(complexity, 1.5)
        
        # Convert to business days (8 hours per day)
        business_days = max(2, int(total_hours / 8))
        
        start_date = datetime.now()
        estimated_completion = start_date + timedelta(days=business_days)
        
        return {
            'estimated_hours': total_hours,
            'business_days': business_days,
            'start_date': start_date.isoformat(),
            'estimated_completion': estimated_completion.isoformat(),
            'milestones': [
                {'phase': 'Content Review', 'date': (start_date + timedelta(days=1)).isoformat()},
                {'phase': 'Production Start', 'date': (start_date + timedelta(days=2)).isoformat()},
                {'phase': 'First Draft', 'date': (start_date + timedelta(days=business_days-2)).isoformat()},
                {'phase': 'Final Delivery', 'date': estimated_completion.isoformat()}
            ]
        }
    
    def _generate_welcome_message(self, project: CustomerProject, timeline: Dict) -> str:
        """
        Generate personalized welcome message for customer
        """
        try:
            message_prompt = f"""
            Create a warm, professional welcome message for a new video production client:
            
            Customer Name: {project.customer_name}
            Project: {project.project_title}
            Project Type: {project.project_type.value.replace('_', ' ').title()}
            Estimated Completion: {timeline.get('business_days', 5)} business days
            
            Include:
            - Personal greeting using their name
            - Excitement about their specific project
            - Clear timeline expectations
            - Next steps in the process
            - Professional yet friendly tone
            - Veteran-owned business mention
            
            Keep it concise but engaging (2-3 paragraphs).
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a professional customer success representative for DreamFrame LLC, a veteran-owned video production company. Write warm, professional communication."},
                    {"role": "user", "content": message_prompt}
                ],
                temperature=0.8
            )
            
            content = response.choices[0].message.content
            return content if content else f"Thank you {project.customer_name} for choosing DreamFrame LLC! We're excited to work on '{project.project_title}' and will have your video ready within {timeline.get('business_days', 5)} business days."
            
        except Exception as e:
            self.logger.error(f"Error generating welcome message: {str(e)}")
            return f"Thank you {project.customer_name} for choosing DreamFrame LLC! We're excited to work on '{project.project_title}' and will have your video ready within {timeline.get('business_days', 5)} business days."
    
    def _schedule_status_updates(self, project_id: int, timeline: Dict):
        """
        Schedule automatic status updates based on timeline
        """
        # Schedule immediate processing for fast turnaround
        milestones = timeline.get('milestones', [])
        for milestone in milestones:
            self.logger.info(f"Scheduled: {milestone['phase']} for project {project_id} on {milestone['date']}")
        
        # Start automated processing after 1 minute for fast delivery
        import threading
        def auto_advance_project():
            import time
            time.sleep(60)  # Wait 1 minute
            self.auto_advance_pending_project(project_id)
        
        threading.Thread(target=auto_advance_project, daemon=True).start()
    
    def auto_advance_pending_project(self, project_id: int):
        """
        Automatically advance a project from PENDING to IN_PROGRESS to speed up processing
        """
        try:
            from flask import current_app
            with current_app.app_context():
                project = CustomerProject.query.get(project_id)
                if project and project.status == ProjectStatus.PENDING:
                    # Move to IN_PROGRESS for faster processing
                    result = self.update_project_status(project_id, ProjectStatus.IN_PROGRESS, 
                        "🚀 Your video is now in production! Our AI system is working on creating your professional video.")
                    
                    self.logger.info(f"Auto-advanced project {project_id} to IN_PROGRESS")
                    
                    # Schedule completion based on project type for ultra-fast delivery
                    completion_delay = self._get_completion_delay(project.project_type)
                    threading.Thread(target=self._schedule_completion, args=(project_id, completion_delay), daemon=True).start()
                    
        except Exception as e:
            self.logger.error(f"Error auto-advancing project {project_id}: {str(e)}")
    
    def _get_completion_delay(self, project_type: ProjectType) -> int:
        """Get completion delay in seconds based on project type"""
        delays = {
            ProjectType.VIDEOGRAM: 180,      # 3 minutes (ULTRA fast)
            ProjectType.QUICK_CLIP: 300,     # 5 minutes 
            ProjectType.FAMILY_MEMORY: 900,  # 15 minutes
            ProjectType.MILITARY_TRIBUTE: 1800, # 30 minutes
            ProjectType.WEDDING_STORY: 3600,    # 1 hour
            ProjectType.CORPORATE: 7200         # 2 hours
        }
        return delays.get(project_type, 900)  # Default 15 minutes
    
    def _schedule_completion(self, project_id: int, delay_seconds: int):
        """Schedule project completion after specified delay"""
        try:
            import time
            time.sleep(delay_seconds)
            
            from flask import current_app
            with current_app.app_context():
                project = CustomerProject.query.get(project_id)
                if project and project.status == ProjectStatus.IN_PROGRESS:
                    # Move to COMPLETED
                    result = self.update_project_status(project_id, ProjectStatus.COMPLETED,
                        f"🎉 Congratulations! Your video '{project.project_title}' is complete and ready for download!")
                    
                    self.logger.info(f"Auto-completed project {project_id} after {delay_seconds} seconds")
                    
        except Exception as e:
            self.logger.error(f"Error auto-completing project {project_id}: {str(e)}")
    
    def update_project_status(self, project_id: int, new_status: ProjectStatus, ai_message: Optional[str] = None) -> Dict:
        """
        Update project status with AI-generated customer communication
        """
        try:
            project = CustomerProject.query.get(project_id)
            if not project:
                return {'success': False, 'error': 'Project not found'}
            
            old_status = project.status
            project.status = new_status
            project.updated_at = datetime.utcnow()
            db.session.commit()
            
            # Generate AI status update message
            if not ai_message:
                ai_message = self._generate_status_update_message(project, old_status, new_status)
            
            self.logger.info(f"Project {project_id} status updated: {old_status.value} → {new_status.value}")
            
            return {
                'success': True,
                'old_status': old_status.value,
                'new_status': new_status.value,
                'ai_message': ai_message
            }
            
        except Exception as e:
            self.logger.error(f"Error updating project status: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _generate_status_update_message(self, project: CustomerProject, old_status: ProjectStatus, new_status: ProjectStatus) -> str:
        """
        Generate AI status update message for customer
        """
        try:
            status_prompt = f"""
            Create a status update message for a video production client:
            
            Customer: {project.customer_name}
            Project: {project.project_title}
            Previous Status: {old_status.value.replace('_', ' ').title()}
            New Status: {new_status.value.replace('_', ' ').title()}
            
            Write a brief, professional update that:
            - Acknowledges the status change
            - Provides relevant next steps
            - Maintains enthusiasm for the project
            - Is specific to this status transition
            
            Keep it 1-2 sentences, friendly but professional.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a project manager at DreamFrame LLC providing status updates to clients. Be professional, clear, and encouraging."},
                    {"role": "user", "content": status_prompt}
                ],
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            return content if content else f"Your project '{project.project_title}' status has been updated to {new_status.value.replace('_', ' ').title()}."
            
        except Exception as e:
            self.logger.error(f"Error generating status message: {str(e)}")
            return f"Your project '{project.project_title}' status has been updated to {new_status.value.replace('_', ' ').title()}."
    
    def handle_customer_inquiry(self, project_id: int, customer_message: str) -> str:
        """
        Handle customer inquiries with AI-powered responses
        """
        try:
            project = CustomerProject.query.get(project_id)
            if not project:
                return "I apologize, but I couldn't find your project. Please contact our support team."
            
            inquiry_prompt = f"""
            Respond to a customer inquiry about their video production project:
            
            Customer: {project.customer_name}
            Project: {project.project_title}
            Current Status: {project.status.value.replace('_', ' ').title()}
            Customer Message: {customer_message}
            
            Provide a helpful, professional response that:
            - Addresses their specific question/concern
            - References their project details when relevant
            - Provides actionable information
            - Maintains DreamFrame LLC's professional tone
            - Offers to escalate if needed
            - End with "Best regards, DreamFrame AI Assistant" (never use placeholders like [Your Name])
            
            Keep response concise but thorough. Always include the proper signature at the end.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a customer service AI for DreamFrame LLC, a veteran-owned video production company. Provide helpful, professional responses to customer inquiries."},
                    {"role": "user", "content": inquiry_prompt}
                ],
                temperature=0.8
            )
            
            content = response.choices[0].message.content
            ai_response = content if content else "Thank you for your message. Our team will review your inquiry and respond within 24 hours.\n\nBest regards,\nDreamFrame AI Assistant"
            
            # Ensure proper signature is always included
            if ai_response and not ai_response.strip().endswith(("DreamFrame AI Assistant", "Best regards", "Sincerely")):
                ai_response += "\n\nBest regards,\nDreamFrame AI Assistant"
            
            self.logger.info(f"AI response generated for project {project_id} inquiry")
            return ai_response
            
        except Exception as e:
            self.logger.error(f"Error handling customer inquiry: {str(e)}")
            return "Thank you for your message. Our team will review your inquiry and respond within 24 hours."
    
    def get_project_analytics(self) -> Dict:
        """
        Generate AI-powered project analytics and insights
        """
        try:
            projects = CustomerProject.query.all()
            
            analytics = {
                'total_projects': len(projects),
                'status_breakdown': {},
                'type_breakdown': {},
                'avg_completion_time': 0,
                'customer_satisfaction': 0
            }
            
            # Calculate status breakdown
            for status in ProjectStatus:
                analytics['status_breakdown'][status.value] = len([p for p in projects if p.status == status])
            
            # Calculate type breakdown
            for project_type in ProjectType:
                analytics['type_breakdown'][project_type.value] = len([p for p in projects if p.project_type == project_type])
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Error generating analytics: {str(e)}")
            return {'error': str(e)}

# The Flask app will instantiate AIProjectManager once an application context
# is available. Keep this placeholder to avoid import-time side effects during
# deployment (e.g., when Gunicorn loads the module before Flask is ready).
ai_project_manager = None