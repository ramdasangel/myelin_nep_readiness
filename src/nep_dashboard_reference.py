"""
NEP Readiness Assessment Dashboard - Reference Implementation
=============================================================

This script provides reference functions for implementing the NEP readiness
assessment dashboard in the Myelin platform.

Author: Myelin Educational Technology
Date: January 2026
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple
from datetime import datetime

class NEPAssessmentAnalyzer:
    """
    Main class for NEP readiness assessment analysis
    """
    
    def __init__(self):
        self.fp_labels = {
            'FP1': 'Each Child is Unique',
            'FP2': 'Holistic & Experiential Learning',
            'FP3': 'Teacher as Reflective Practitioner',
            'FP4': 'Assessment for Learning',
            'FP5': 'Collaboration & Community'
        }
        
        self.fp_columns = ['FP1', 'FP2', 'FP3', 'FP4', 'FP5']
        
        # FP mapping for School Leaders (from design document)
        self.leader_fp_mapping = {
            'Q1': {'A': 'FP2', 'B': 'FP3', 'C': 'FP1', 'D': 'FP5'},
            'Q2': {'A': 'FP3', 'B': 'FP1', 'C': 'FP4', 'D': 'FP5'},
            'Q3': {'A': 'FP2', 'B': 'FP3', 'C': 'FP1', 'D': 'FP2'},
            'Q4': {'A': 'FP3', 'B': 'FP4', 'C': 'FP5', 'D': 'FP2'},
            'Q5': {'A': 'FP2', 'B': 'FP4', 'C': 'FP3', 'D': 'FP1'},
            'Q6': {'A': 'FP2', 'B': 'FP3', 'C': 'FP4', 'D': 'FP1'},
            'Q7': {'A': 'FP2', 'B': 'FP2', 'C': 'FP4', 'D': 'FP3'},
            'Q8': {'A': 'FP2', 'B': 'FP4', 'C': 'FP1', 'D': 'FP2'},
            'Q9': {'A': 'FP2', 'B': 'FP4', 'C': 'FP2', 'D': 'FP5'},
            'Q10': {'A': 'FP2', 'B': 'FP1', 'C': 'FP3', 'D': 'FP2'},
            'Q11': {'A': 'FP2', 'B': 'FP3', 'C': 'FP4', 'D': 'FP5'},
            'Q12': {'A': 'FP2', 'B': 'FP5', 'C': 'FP4', 'D': 'FP5'},
            'Q13': {'A': 'FP2', 'B': 'FP4', 'C': 'FP5', 'D': 'FP1'},
            'Q14': {'A': 'FP2', 'B': 'FP2', 'C': 'FP1', 'D': 'FP4'},
            'Q15': {'A': 'FP2', 'B': 'FP3', 'C': 'FP5', 'D': 'FP4'}
        }
        
        # FP mapping for Teachers
        self.teacher_fp_mapping = {
            'Q1': {'A': 'FP2', 'B': 'FP2', 'C': 'FP1', 'D': 'FP5'},
            'Q2': {'A': 'FP4', 'B': 'FP1', 'C': 'FP5', 'D': 'FP2'},
            'Q3': {'A': 'FP2', 'B': 'FP5', 'C': 'FP1', 'D': 'FP2'},
            'Q4': {'A': 'FP2', 'B': 'FP4', 'C': 'FP4', 'D': 'FP5'},
            'Q5': {'A': 'FP2', 'B': 'FP4', 'C': 'FP4', 'D': 'FP5'},
            'Q6': {'A': 'FP2', 'B': 'FP4', 'C': 'FP4', 'D': 'FP4'},
            'Q7': {'A': 'FP2', 'B': 'FP2', 'C': 'FP4', 'D': 'FP3'},
            'Q8': {'A': 'FP2', 'B': 'FP4', 'C': 'FP2', 'D': 'FP2'},
            'Q9': {'A': 'FP2', 'B': 'FP2', 'C': 'FP4', 'D': 'FP2'},
            'Q10': {'A': 'FP2', 'B': 'FP3', 'C': 'FP3', 'D': 'FP3'},
            'Q11': {'A': 'FP2', 'B': 'FP3', 'C': 'FP3', 'D': 'FP3'},
            'Q12': {'A': 'FP2', 'B': 'FP3', 'C': 'FP3', 'D': 'FP3'},
            'Q13': {'A': 'FP2', 'B': 'FP5', 'C': 'FP5', 'D': 'FP5'},
            'Q14': {'A': 'FP2', 'B': 'FP5', 'C': 'FP5', 'D': 'FP5'},
            'Q15': {'A': 'FP2', 'B': 'FP5', 'C': 'FP5', 'D': 'FP5'}
        }
    
    def calculate_fp_scores(self, responses: pd.DataFrame, user_type: str = 'leader') -> pd.DataFrame:
        """
        Calculate FP scores from survey responses
        
        Args:
            responses: DataFrame with columns [user_id, Q1, Q2, ..., Q15]
            user_type: 'leader' or 'teacher'
            
        Returns:
            DataFrame with FP scores added
        """
        df = responses.copy()
        mapping = self.leader_fp_mapping if user_type == 'leader' else self.teacher_fp_mapping
        
        # Initialize FP columns
        for fp in self.fp_columns:
            df[fp] = 0
        
        # Calculate scores
        for idx, row in df.iterrows():
            for q in range(1, 16):
                q_col = f'Q{q}'
                answer = row[q_col]
                fp = mapping[q_col][answer]
                df.at[idx, fp] += 1
        
        return df
    
    def get_fp_interpretation(self, score: int) -> Dict[str, str]:
        """
        Get interpretation of FP score
        
        Args:
            score: FP score (0-15)
            
        Returns:
            Dictionary with level and description
        """
        if score >= 12:
            return {
                'level': 'Strong',
                'description': 'Demonstrates strong alignment with this NEP principle',
                'color': '#2ecc71'
            }
        elif score >= 8:
            return {
                'level': 'Moderate',
                'description': 'Shows moderate understanding; continue building on this foundation',
                'color': '#f39c12'
            }
        elif score >= 4:
            return {
                'level': 'Developing',
                'description': 'Developing awareness; needs focused support and training',
                'color': '#e67e22'
            }
        else:
            return {
                'level': 'Limited',
                'description': 'Limited alignment; requires immediate intervention and development',
                'color': '#e74c3c'
            }
    
    def generate_user_profile(self, user_id: str, user_data: pd.DataFrame) -> Dict:
        """
        Generate comprehensive profile for a user
        
        Args:
            user_id: User identifier
            user_data: DataFrame with user's responses and FP scores
            
        Returns:
            Dictionary with profile information
        """
        user = user_data[user_data.iloc[:, 0] == user_id].iloc[0]
        
        fp_scores = {fp: int(user[fp]) for fp in self.fp_columns}
        
        profile = {
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'fp_scores': fp_scores,
            'total_score': sum(fp_scores.values()),
            'interpretations': {},
            'top_strength': max(fp_scores, key=fp_scores.get),
            'development_area': min(fp_scores, key=fp_scores.get),
            'recommendations': []
        }
        
        # Add interpretations for each FP
        for fp, score in fp_scores.items():
            profile['interpretations'][fp] = self.get_fp_interpretation(score)
        
        # Generate recommendations
        profile['recommendations'] = self.generate_recommendations(fp_scores)
        
        return profile
    
    def generate_recommendations(self, fp_scores: Dict[str, int]) -> List[Dict]:
        """
        Generate personalized recommendations based on FP scores
        
        Args:
            fp_scores: Dictionary of FP scores
            
        Returns:
            List of recommendation dictionaries
        """
        recommendations = []
        
        for fp, score in fp_scores.items():
            if score < 5:
                recommendations.append({
                    'fp': fp,
                    'priority': 'High',
                    'action': self._get_recommendation_for_fp(fp, 'high'),
                    'resources': self._get_resources_for_fp(fp)
                })
            elif score < 8:
                recommendations.append({
                    'fp': fp,
                    'priority': 'Medium',
                    'action': self._get_recommendation_for_fp(fp, 'medium'),
                    'resources': self._get_resources_for_fp(fp)
                })
        
        return recommendations
    
    def _get_recommendation_for_fp(self, fp: str, priority: str) -> str:
        """Get specific recommendation text"""
        recommendations = {
            'FP1': {
                'high': 'Enroll in "Differentiated Instruction" workshop. Practice observing and documenting individual student learning patterns.',
                'medium': 'Implement at least one differentiated activity per week. Maintain student learning journals.'
            },
            'FP2': {
                'high': 'Attend "Experiential Learning Design" training. Start with one hands-on activity per chapter.',
                'medium': 'Increase use of real-world examples and project-based learning in lessons.'
            },
            'FP3': {
                'high': 'Join monthly peer reflection circles. Maintain a teaching journal with weekly reflections.',
                'medium': 'Engage in peer observations and feedback sessions twice per term.'
            },
            'FP4': {
                'high': 'Complete "Formative Assessment Strategies" course. Design exit tickets for every lesson.',
                'medium': 'Implement weekly informal assessments to track student progress.'
            },
            'FP5': {
                'high': 'Design a parent engagement program. Conduct monthly parent-teacher collaboration sessions.',
                'medium': 'Share learning updates with parents fortnightly. Create home learning activity guides.'
            }
        }
        return recommendations.get(fp, {}).get(priority, 'Continue developing this area.')
    
    def _get_resources_for_fp(self, fp: str) -> List[str]:
        """Get learning resources for each FP"""
        resources = {
            'FP1': [
                'NEP 2020 Section 4.2 - Individual Learning',
                'Book: "The Differentiated Classroom" by Carol Ann Tomlinson',
                'Myelin Course: Understanding Learner Diversity'
            ],
            'FP2': [
                'NCF 2005 Chapter 3 - Learning Process',
                'Workshop: Designing Experiential Learning Activities',
                'Myelin Course: Project-Based Learning Fundamentals'
            ],
            'FP3': [
                'NEP 2020 Chapter 5 - Teacher Education',
                'Book: "Reflective Teaching" by Andrew Pollard',
                'Myelin Course: Reflective Practice for Educators'
            ],
            'FP4': [
                'NEP 2020 Sections 4.34-4.38 - Assessment Reform',
                'Workshop: Formative Assessment Techniques',
                'Myelin Course: Competency-Based Assessment'
            ],
            'FP5': [
                'NEP 2020 Section 6 - Community Engagement',
                'Workshop: Building Parent-Teacher Partnerships',
                'Myelin Course: Effective Parent Communication'
            ]
        }
        return resources.get(fp, [])
    
    def create_radar_chart(self, fp_scores: Dict[str, int], user_id: str, 
                          cohort_avg: Dict[str, float] = None) -> plt.Figure:
        """
        Create radar chart for FP scores
        
        Args:
            fp_scores: Dictionary of user's FP scores
            user_id: User identifier
            cohort_avg: Optional cohort average for comparison
            
        Returns:
            Matplotlib figure
        """
        categories = [self.fp_labels[fp] for fp in self.fp_columns]
        
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        
        user_scores = [fp_scores[fp] for fp in self.fp_columns]
        user_scores += user_scores[:1]
        angles += angles[:1]
        
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
        
        # Plot user scores
        ax.plot(angles, user_scores, 'o-', linewidth=2, label=user_id, color='#3498db')
        ax.fill(angles, user_scores, alpha=0.25, color='#3498db')
        
        # Plot cohort average if provided
        if cohort_avg:
            cohort_scores = [cohort_avg[fp] for fp in self.fp_columns]
            cohort_scores += cohort_scores[:1]
            ax.plot(angles, cohort_scores, 'o--', linewidth=2, label='Cohort Average', 
                   color='#95a5a6', alpha=0.7)
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, size=10)
        ax.set_ylim(0, 15)
        ax.set_yticks([3, 6, 9, 12, 15])
        ax.set_yticklabels(['3', '6', '9', '12', '15'])
        ax.grid(True)
        
        ax.set_title(f'NEP Readiness Profile: {user_id}', size=16, fontweight='bold', pad=20)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
        
        plt.tight_layout()
        return fig
    
    def create_cohort_heatmap(self, data: pd.DataFrame, title: str = 'Cohort NEP Readiness') -> plt.Figure:
        """
        Create heatmap for entire cohort
        
        Args:
            data: DataFrame with FP scores
            title: Chart title
            
        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=(12, max(8, len(data) * 0.4)))
        
        fp_data = data[self.fp_columns]
        user_ids = data.iloc[:, 0].values
        
        sns.heatmap(fp_data, annot=True, fmt='d', cmap='RdYlGn', 
                   cbar_kws={'label': 'Score (out of 15)'}, 
                   yticklabels=user_ids, xticklabels=[self.fp_labels[fp] for fp in self.fp_columns],
                   vmin=0, vmax=15, ax=ax, linewidths=0.5, linecolor='gray')
        
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('NEP Foundational Philosophy', fontsize=12, fontweight='bold')
        ax.set_ylabel('User ID', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        return fig
    
    def generate_cohort_summary(self, data: pd.DataFrame, cohort_name: str) -> Dict:
        """
        Generate summary statistics for a cohort
        
        Args:
            data: DataFrame with FP scores
            cohort_name: Name of the cohort
            
        Returns:
            Dictionary with summary statistics
        """
        fp_data = data[self.fp_columns]
        
        summary = {
            'cohort_name': cohort_name,
            'n': len(data),
            'timestamp': datetime.now().isoformat(),
            'fp_averages': fp_data.mean().to_dict(),
            'fp_std': fp_data.std().to_dict(),
            'fp_min': fp_data.min().to_dict(),
            'fp_max': fp_data.max().to_dict(),
            'top_strength': fp_data.mean().idxmax(),
            'development_area': fp_data.mean().idxmin(),
            'distribution': {}
        }
        
        # Calculate distribution by readiness level
        for fp in self.fp_columns:
            scores = fp_data[fp]
            summary['distribution'][fp] = {
                'strong': len(scores[scores >= 12]),
                'moderate': len(scores[(scores >= 8) & (scores < 12)]),
                'developing': len(scores[(scores >= 4) & (scores < 8)]),
                'limited': len(scores[scores < 4])
            }
        
        return summary
    
    def compare_cohorts(self, cohort1: pd.DataFrame, cohort2: pd.DataFrame,
                       name1: str = 'Cohort 1', name2: str = 'Cohort 2') -> plt.Figure:
        """
        Compare two cohorts side by side
        
        Args:
            cohort1: First cohort data
            cohort2: Second cohort data
            name1: Name of first cohort
            name2: Name of second cohort
            
        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        fp_means1 = cohort1[self.fp_columns].mean()
        fp_means2 = cohort2[self.fp_columns].mean()
        
        x = np.arange(len(self.fp_columns))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, fp_means1, width, label=name1, 
                      color='#3498db', edgecolor='black', linewidth=1.5)
        bars2 = ax.bar(x + width/2, fp_means2, width, label=name2,
                      color='#e74c3c', edgecolor='black', linewidth=1.5)
        
        ax.set_ylabel('Average Score (out of 15)', fontsize=12, fontweight='bold')
        ax.set_xlabel('NEP Foundational Philosophy', fontsize=12, fontweight='bold')
        ax.set_title(f'Cohort Comparison: {name1} vs {name2}', fontsize=16, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels([self.fp_labels[fp] for fp in self.fp_columns], rotation=45, ha='right')
        ax.legend()
        ax.set_ylim(0, 15)
        ax.grid(axis='y', alpha=0.3)
        
        # Add value labels on bars
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.1f}', ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        return fig


# Example usage functions

def example_individual_analysis():
    """Example: Analyze individual user"""
    analyzer = NEPAssessmentAnalyzer()
    
    # Load data
    data = pd.read_csv('school_leaders_responses_with_fp.csv')
    
    # Generate profile for user L01
    profile = analyzer.generate_user_profile('L01', data)
    
    print("User Profile:")
    print(f"User ID: {profile['user_id']}")
    print(f"FP Scores: {profile['fp_scores']}")
    print(f"Top Strength: {profile['top_strength']}")
    print(f"Development Area: {profile['development_area']}")
    print("\nRecommendations:")
    for rec in profile['recommendations']:
        print(f"  - {rec['fp']} ({rec['priority']} Priority): {rec['action']}")
    
    # Create radar chart
    fig = analyzer.create_radar_chart(profile['fp_scores'], 'L01')
    fig.savefig('user_profile_radar.png', dpi=300, bbox_inches='tight')
    print("\nRadar chart saved as user_profile_radar.png")


def example_cohort_analysis():
    """Example: Analyze entire cohort"""
    analyzer = NEPAssessmentAnalyzer()
    
    # Load data
    data = pd.read_csv('school_leaders_responses_with_fp.csv')
    
    # Generate cohort summary
    summary = analyzer.generate_cohort_summary(data, 'School Leaders 2026')
    
    print("Cohort Summary:")
    print(f"Cohort: {summary['cohort_name']}")
    print(f"Size: {summary['n']} respondents")
    print(f"\nAverage FP Scores:")
    for fp, score in summary['fp_averages'].items():
        print(f"  {fp}: {score:.2f}")
    
    # Create heatmap
    fig = analyzer.create_cohort_heatmap(data, 'School Leaders NEP Readiness')
    fig.savefig('cohort_heatmap.png', dpi=300, bbox_inches='tight')
    print("\nHeatmap saved as cohort_heatmap.png")


def example_comparison():
    """Example: Compare leaders vs teachers"""
    analyzer = NEPAssessmentAnalyzer()
    
    # Load data
    leaders_data = pd.read_csv('school_leaders_responses_with_fp.csv')
    teachers_data = pd.read_csv('teachers_responses_with_fp.csv')
    
    # Compare cohorts
    fig = analyzer.compare_cohorts(leaders_data, teachers_data, 
                                   'School Leaders', 'Teachers')
    fig.savefig('leaders_vs_teachers.png', dpi=300, bbox_inches='tight')
    print("Comparison chart saved as leaders_vs_teachers.png")


if __name__ == '__main__':
    print("NEP Readiness Assessment Analyzer - Reference Implementation")
    print("=" * 70)
    print("\nThis script provides reference functions for dashboard development.")
    print("\nUncomment example functions below to test:")
    print("  - example_individual_analysis()")
    print("  - example_cohort_analysis()")
    print("  - example_comparison()")
    
    # Uncomment to run examples:
    # example_individual_analysis()
    # example_cohort_analysis()
    # example_comparison()
