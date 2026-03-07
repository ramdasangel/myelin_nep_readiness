"""
NEP Readiness Dashboard Generator
=================================

Accepts JSON input with school branch responses (Leaders or Teachers)
and generates a comprehensive NEP readiness dashboard.

Usage:
    python nep_dashboard_generator.py input.json [--output-dir ./output]

Or programmatically:
    from nep_dashboard_generator import NEPDashboardGenerator
    generator = NEPDashboardGenerator()
    result = generator.generate_dashboard(json_data)
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from matplotlib.patches import Patch


@dataclass
class ResponseValidationResult:
    """Result of validating a single response"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]


@dataclass
class InputValidationResult:
    """Result of validating the entire JSON input"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    response_count: int
    user_type: str


class NEPDashboardGenerator:
    """
    Main class for generating NEP readiness dashboards from JSON input.
    """

    # FP Labels
    FP_LABELS = {
        'FP1': 'Each Child is Unique',
        'FP2': 'Holistic & Experiential Learning',
        'FP3': 'Teacher as Reflective Practitioner',
        'FP4': 'Assessment for Learning',
        'FP5': 'Collaboration & Community'
    }

    FP_SHORT_LABELS = {
        'FP1': 'Each Child\nUnique',
        'FP2': 'Holistic\nLearning',
        'FP3': 'Reflective\nPractice',
        'FP4': 'Assessment\nfor Learning',
        'FP5': 'Collaboration\n& Community'
    }

    FP_COLUMNS = ['FP1', 'FP2', 'FP3', 'FP4', 'FP5']

    # Color scheme
    COLORS = {
        'strong': '#27ae60',      # Green
        'moderate': '#f39c12',    # Orange
        'developing': '#e67e22',  # Dark orange
        'limited': '#e74c3c',     # Red
        'primary': '#3498db',     # Blue
        'secondary': '#9b59b6',   # Purple
        'background': '#ecf0f1',  # Light gray
    }

    # FP mapping for School Leaders
    LEADER_FP_MAPPING = {
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
    TEACHER_FP_MAPPING = {
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

    def __init__(self):
        """Initialize the dashboard generator"""
        plt.style.use('seaborn-v0_8-whitegrid')

    def validate_input(self, data: Dict) -> InputValidationResult:
        """
        Validate the JSON input structure and content.

        Args:
            data: Parsed JSON data

        Returns:
            InputValidationResult with validation status and messages
        """
        errors = []
        warnings = []

        # Check required fields
        required_fields = ['school_branch', 'user_type', 'responses']
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: '{field}'")

        if errors:
            return InputValidationResult(
                is_valid=False, errors=errors, warnings=warnings,
                response_count=0, user_type=''
            )

        # Validate user_type
        user_type = data['user_type'].lower()
        if user_type not in ['leader', 'teacher']:
            errors.append(f"Invalid user_type: '{data['user_type']}'. Must be 'leader' or 'teacher'")

        # Validate responses
        responses = data['responses']
        if not isinstance(responses, list):
            errors.append("'responses' must be a list")
        elif len(responses) == 0:
            errors.append("'responses' list is empty")
        else:
            # Validate each response
            valid_answers = {'A', 'B', 'C', 'D'}
            for i, resp in enumerate(responses):
                if 'user_id' not in resp:
                    errors.append(f"Response {i+1}: Missing 'user_id'")

                # Check all 15 questions
                for q in range(1, 16):
                    q_key = f'Q{q}'
                    if q_key not in resp:
                        errors.append(f"Response {i+1} ({resp.get('user_id', 'unknown')}): Missing '{q_key}'")
                    elif resp[q_key].upper() not in valid_answers:
                        errors.append(f"Response {i+1}: Invalid answer '{resp[q_key]}' for {q_key}. Must be A, B, C, or D")

        # Warnings
        if 'assessment_date' not in data:
            warnings.append("No 'assessment_date' provided. Using current date.")

        if 'school_branch' in data and isinstance(data['school_branch'], dict):
            if 'name' not in data['school_branch']:
                warnings.append("school_branch.name not provided")

        return InputValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            response_count=len(data.get('responses', [])),
            user_type=user_type if len(errors) == 0 else ''
        )

    def calculate_fp_scores(self, responses: List[Dict], user_type: str) -> pd.DataFrame:
        """
        Calculate FP scores from responses.

        Args:
            responses: List of response dictionaries
            user_type: 'leader' or 'teacher'

        Returns:
            DataFrame with responses and FP scores
        """
        mapping = self.LEADER_FP_MAPPING if user_type == 'leader' else self.TEACHER_FP_MAPPING

        results = []
        for resp in responses:
            row = {'user_id': resp['user_id']}

            # Copy question responses and calculate FP mappings
            fp_counts = {fp: 0 for fp in self.FP_COLUMNS}

            for q in range(1, 16):
                q_key = f'Q{q}'
                answer = resp[q_key].upper()
                row[q_key] = answer

                # Map to FP
                fp = mapping[q_key][answer]
                row[f'{q_key}_FP'] = fp
                fp_counts[fp] += 1

            # Add FP totals
            for fp, count in fp_counts.items():
                row[fp] = count

            results.append(row)

        return pd.DataFrame(results)

    def get_interpretation(self, score: int) -> Dict[str, str]:
        """Get interpretation for an FP score"""
        if score >= 12:
            return {'level': 'Strong', 'color': self.COLORS['strong']}
        elif score >= 8:
            return {'level': 'Moderate', 'color': self.COLORS['moderate']}
        elif score >= 4:
            return {'level': 'Developing', 'color': self.COLORS['developing']}
        else:
            return {'level': 'Limited', 'color': self.COLORS['limited']}

    def generate_recommendations(self, fp_scores: Dict[str, float]) -> List[Dict]:
        """Generate recommendations based on FP scores"""
        recommendations = {
            'FP1': {
                'high': 'Enroll in "Differentiated Instruction" workshop. Practice observing individual student learning patterns.',
                'medium': 'Implement at least one differentiated activity per week. Maintain student learning journals.'
            },
            'FP2': {
                'high': 'Attend "Experiential Learning Design" training. Start with one hands-on activity per chapter.',
                'medium': 'Increase use of real-world examples and project-based learning.'
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

        result = []
        for fp, score in fp_scores.items():
            if score < 5:
                result.append({
                    'fp': fp,
                    'fp_name': self.FP_LABELS[fp],
                    'priority': 'High',
                    'score': score,
                    'action': recommendations[fp]['high']
                })
            elif score < 8:
                result.append({
                    'fp': fp,
                    'fp_name': self.FP_LABELS[fp],
                    'priority': 'Medium',
                    'score': score,
                    'action': recommendations[fp]['medium']
                })

        return sorted(result, key=lambda x: x['score'])

    def create_dashboard(self, df: pd.DataFrame, metadata: Dict) -> plt.Figure:
        """
        Create a comprehensive dashboard figure.

        Args:
            df: DataFrame with responses and FP scores
            metadata: Dictionary with school_branch, user_type, etc.

        Returns:
            Matplotlib figure
        """
        fig = plt.figure(figsize=(20, 16))
        gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.35, wspace=0.3)

        # Title
        school_name = metadata.get('school_branch', {}).get('name', 'School Branch')
        user_type = metadata['user_type'].title()
        assessment_date = metadata.get('assessment_date', datetime.now().strftime('%Y-%m-%d'))

        fig.suptitle(
            f'NEP Readiness Dashboard - {school_name}\n{user_type}s Assessment ({assessment_date})',
            fontsize=18, fontweight='bold', y=0.98
        )

        # 1. FP Distribution Heatmap (top-left, spans 2 columns)
        ax1 = fig.add_subplot(gs[0, :2])
        self._plot_heatmap(ax1, df)

        # 2. Average FP Scores Bar Chart (top-right)
        ax2 = fig.add_subplot(gs[0, 2])
        self._plot_average_scores(ax2, df)

        # 3. FP Distribution Box Plot (middle-left)
        ax3 = fig.add_subplot(gs[1, 0])
        self._plot_boxplot(ax3, df)

        # 4. Radar Chart for Cohort Average (middle-center)
        ax4 = fig.add_subplot(gs[1, 1], projection='polar')
        self._plot_radar(ax4, df)

        # 5. Readiness Level Distribution (middle-right)
        ax5 = fig.add_subplot(gs[1, 2])
        self._plot_readiness_distribution(ax5, df)

        # 6. Individual Scores Scatter (bottom-left)
        ax6 = fig.add_subplot(gs[2, 0])
        self._plot_total_scores(ax6, df)

        # 7. Summary Statistics Table (bottom-center)
        ax7 = fig.add_subplot(gs[2, 1])
        self._plot_summary_table(ax7, df, metadata)

        # 8. Top Recommendations (bottom-right)
        ax8 = fig.add_subplot(gs[2, 2])
        self._plot_recommendations(ax8, df)

        return fig

    def _plot_heatmap(self, ax: plt.Axes, df: pd.DataFrame):
        """Plot FP scores heatmap"""
        fp_data = df[self.FP_COLUMNS].values
        user_ids = df['user_id'].values

        # Limit to 20 users for readability
        if len(user_ids) > 20:
            sample_idx = np.linspace(0, len(user_ids)-1, 20, dtype=int)
            fp_data = fp_data[sample_idx]
            user_ids = user_ids[sample_idx]

        im = ax.imshow(fp_data, cmap='RdYlGn', aspect='auto', vmin=0, vmax=15)

        ax.set_xticks(range(5))
        ax.set_xticklabels([self.FP_SHORT_LABELS[fp] for fp in self.FP_COLUMNS], fontsize=9)
        ax.set_yticks(range(len(user_ids)))
        ax.set_yticklabels(user_ids, fontsize=8)

        # Add colorbar
        cbar = plt.colorbar(im, ax=ax, shrink=0.8)
        cbar.set_label('Score (0-15)', fontsize=10)

        # Add values to cells
        for i in range(len(user_ids)):
            for j in range(5):
                val = fp_data[i, j]
                color = 'white' if val < 7 or val > 10 else 'black'
                ax.text(j, i, str(int(val)), ha='center', va='center',
                       fontsize=8, color=color, fontweight='bold')

        ax.set_title('Individual FP Scores Heatmap', fontsize=12, fontweight='bold', pad=10)

    def _plot_average_scores(self, ax: plt.Axes, df: pd.DataFrame):
        """Plot average FP scores bar chart"""
        means = df[self.FP_COLUMNS].mean()

        colors = [self.get_interpretation(score)['color'] for score in means]
        bars = ax.bar(range(5), means, color=colors, edgecolor='black', linewidth=1.5)

        ax.set_xticks(range(5))
        ax.set_xticklabels([self.FP_SHORT_LABELS[fp] for fp in self.FP_COLUMNS], fontsize=8)
        ax.set_ylabel('Average Score', fontsize=10)
        ax.set_ylim(0, 15)
        ax.axhline(y=8, color='gray', linestyle='--', alpha=0.5, label='Moderate threshold')
        ax.axhline(y=4, color='gray', linestyle=':', alpha=0.5, label='Developing threshold')

        # Add value labels
        for bar, val in zip(bars, means):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                   f'{val:.1f}', ha='center', va='bottom', fontsize=9, fontweight='bold')

        ax.set_title('Average FP Scores', fontsize=12, fontweight='bold', pad=10)
        ax.legend(loc='upper right', fontsize=8)

    def _plot_boxplot(self, ax: plt.Axes, df: pd.DataFrame):
        """Plot FP score distributions as box plots"""
        fp_data = df[self.FP_COLUMNS]

        bp = ax.boxplot([fp_data[fp] for fp in self.FP_COLUMNS],
                        patch_artist=True, tick_labels=['FP1', 'FP2', 'FP3', 'FP4', 'FP5'])

        colors = [self.COLORS['primary'], self.COLORS['secondary'], '#1abc9c', '#e74c3c', '#f39c12']
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)

        ax.set_ylabel('Score', fontsize=10)
        ax.set_ylim(0, 15)
        ax.set_title('Score Distribution by FP', fontsize=12, fontweight='bold', pad=10)

    def _plot_radar(self, ax: plt.Axes, df: pd.DataFrame):
        """Plot radar chart for cohort average"""
        means = df[self.FP_COLUMNS].mean().values

        angles = np.linspace(0, 2 * np.pi, 5, endpoint=False).tolist()
        means_plot = np.concatenate([means, [means[0]]])
        angles_plot = angles + [angles[0]]

        ax.plot(angles_plot, means_plot, 'o-', linewidth=2, color=self.COLORS['primary'])
        ax.fill(angles_plot, means_plot, alpha=0.25, color=self.COLORS['primary'])

        ax.set_xticks(angles)
        ax.set_xticklabels(['FP1', 'FP2', 'FP3', 'FP4', 'FP5'], fontsize=10)
        ax.set_ylim(0, 15)
        ax.set_yticks([5, 10, 15])

        ax.set_title('Cohort Average Profile', fontsize=12, fontweight='bold', pad=20)

    def _plot_readiness_distribution(self, ax: plt.Axes, df: pd.DataFrame):
        """Plot stacked bar for readiness level distribution"""
        levels = {'Strong': [], 'Moderate': [], 'Developing': [], 'Limited': []}

        for fp in self.FP_COLUMNS:
            scores = df[fp]
            levels['Strong'].append(len(scores[scores >= 12]))
            levels['Moderate'].append(len(scores[(scores >= 8) & (scores < 12)]))
            levels['Developing'].append(len(scores[(scores >= 4) & (scores < 8)]))
            levels['Limited'].append(len(scores[scores < 4]))

        x = np.arange(5)
        width = 0.6

        bottom = np.zeros(5)
        colors = [self.COLORS['strong'], self.COLORS['moderate'],
                  self.COLORS['developing'], self.COLORS['limited']]

        for (level, counts), color in zip(levels.items(), colors):
            ax.bar(x, counts, width, label=level, bottom=bottom, color=color)
            bottom += np.array(counts)

        ax.set_xticks(x)
        ax.set_xticklabels(['FP1', 'FP2', 'FP3', 'FP4', 'FP5'], fontsize=9)
        ax.set_ylabel('Number of Users', fontsize=10)
        ax.legend(loc='upper right', fontsize=8)
        ax.set_title('Readiness Level Distribution', fontsize=12, fontweight='bold', pad=10)

    def _plot_total_scores(self, ax: plt.Axes, df: pd.DataFrame):
        """Plot total scores distribution"""
        # Calculate dominant FP for each user
        total_fp_per_user = df[self.FP_COLUMNS].sum(axis=1)  # Should always be 15
        dominant_fp = df[self.FP_COLUMNS].idxmax(axis=1)

        fp_colors = {
            'FP1': self.COLORS['primary'],
            'FP2': self.COLORS['secondary'],
            'FP3': '#1abc9c',
            'FP4': '#e74c3c',
            'FP5': '#f39c12'
        }

        colors = [fp_colors[fp] for fp in dominant_fp]

        ax.scatter(range(len(df)), df[self.FP_COLUMNS].max(axis=1), c=colors, s=60, alpha=0.7)
        ax.set_xlabel('User Index', fontsize=10)
        ax.set_ylabel('Highest FP Score', fontsize=10)
        ax.set_ylim(0, 15)

        # Add legend
        legend_elements = [Patch(facecolor=fp_colors[fp], label=fp) for fp in self.FP_COLUMNS]
        ax.legend(handles=legend_elements, loc='lower right', fontsize=8, title='Dominant FP')

        ax.set_title('Dominant FP by User', fontsize=12, fontweight='bold', pad=10)

    def _plot_summary_table(self, ax: plt.Axes, df: pd.DataFrame, metadata: Dict):
        """Plot summary statistics as a table"""
        ax.axis('off')

        n_users = len(df)
        fp_means = df[self.FP_COLUMNS].mean()
        fp_std = df[self.FP_COLUMNS].std()

        top_fp = fp_means.idxmax()
        bottom_fp = fp_means.idxmin()

        table_data = [
            ['Total Respondents', str(n_users)],
            ['Assessment Date', metadata.get('assessment_date', datetime.now().strftime('%Y-%m-%d'))],
            ['', ''],
            ['Top Strength', f'{top_fp}: {fp_means[top_fp]:.1f}'],
            ['Development Area', f'{bottom_fp}: {fp_means[bottom_fp]:.1f}'],
            ['', ''],
            ['FP1 Avg (±SD)', f'{fp_means["FP1"]:.1f} (±{fp_std["FP1"]:.1f})'],
            ['FP2 Avg (±SD)', f'{fp_means["FP2"]:.1f} (±{fp_std["FP2"]:.1f})'],
            ['FP3 Avg (±SD)', f'{fp_means["FP3"]:.1f} (±{fp_std["FP3"]:.1f})'],
            ['FP4 Avg (±SD)', f'{fp_means["FP4"]:.1f} (±{fp_std["FP4"]:.1f})'],
            ['FP5 Avg (±SD)', f'{fp_means["FP5"]:.1f} (±{fp_std["FP5"]:.1f})'],
        ]

        table = ax.table(cellText=table_data, loc='center', cellLoc='left',
                        colWidths=[0.5, 0.5])
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 1.5)

        # Style header rows
        for i in [0, 1, 3, 4]:
            table[(i, 0)].set_text_props(fontweight='bold')

        ax.set_title('Summary Statistics', fontsize=12, fontweight='bold', pad=10)

    def _plot_recommendations(self, ax: plt.Axes, df: pd.DataFrame):
        """Plot top recommendations"""
        ax.axis('off')

        fp_means = df[self.FP_COLUMNS].mean().to_dict()
        recommendations = self.generate_recommendations(fp_means)

        if not recommendations:
            ax.text(0.5, 0.5, 'All FP scores are at moderate\nor strong levels.\n\nContinue current practices!',
                   ha='center', va='center', fontsize=11, transform=ax.transAxes,
                   bbox=dict(boxstyle='round', facecolor=self.COLORS['strong'], alpha=0.3))
        else:
            text = "Priority Actions:\n\n"
            for i, rec in enumerate(recommendations[:3]):
                priority_marker = '[HIGH]' if rec['priority'] == 'High' else '[MED]'
                text += f"{priority_marker} {rec['fp_name']}\n"
                text += f"   Score: {rec['score']:.1f}/15\n"
                text += f"   {rec['action'][:60]}...\n\n"

            ax.text(0.05, 0.95, text, ha='left', va='top', fontsize=9,
                   transform=ax.transAxes, family='monospace',
                   bbox=dict(boxstyle='round', facecolor=self.COLORS['background'], alpha=0.5))

        ax.set_title('Top Recommendations', fontsize=12, fontweight='bold', pad=10)

    def generate_dashboard(self, json_data: Dict, output_dir: str = './output') -> Dict:
        """
        Main method to generate dashboard from JSON input.

        Args:
            json_data: Parsed JSON data with responses
            output_dir: Directory to save outputs

        Returns:
            Dictionary with results and file paths
        """
        # Validate input
        validation = self.validate_input(json_data)

        if not validation.is_valid:
            return {
                'success': False,
                'errors': validation.errors,
                'warnings': validation.warnings
            }

        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Calculate FP scores
        df = self.calculate_fp_scores(json_data['responses'], validation.user_type)

        # Prepare metadata
        metadata = {
            'school_branch': json_data.get('school_branch', {}),
            'user_type': validation.user_type,
            'assessment_date': json_data.get('assessment_date', datetime.now().strftime('%Y-%m-%d')),
            'n_respondents': validation.response_count
        }

        # Generate dashboard figure
        fig = self.create_dashboard(df, metadata)

        # Generate file names
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        school_slug = json_data.get('school_branch', {}).get('name', 'school').replace(' ', '_').lower()
        base_name = f"nep_dashboard_{school_slug}_{validation.user_type}s_{timestamp}"

        # Save dashboard image
        dashboard_path = os.path.join(output_dir, f"{base_name}.png")
        fig.savefig(dashboard_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig)

        # Save detailed data CSV
        csv_path = os.path.join(output_dir, f"{base_name}_detailed.csv")
        df.to_csv(csv_path, index=False)

        # Generate summary JSON
        summary = self._generate_summary(df, metadata, validation.warnings)
        summary_path = os.path.join(output_dir, f"{base_name}_summary.json")
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)

        return {
            'success': True,
            'warnings': validation.warnings,
            'files': {
                'dashboard': dashboard_path,
                'data_csv': csv_path,
                'summary_json': summary_path
            },
            'summary': summary
        }

    def _generate_summary(self, df: pd.DataFrame, metadata: Dict, warnings: List[str]) -> Dict:
        """Generate summary statistics dictionary"""
        fp_means = df[self.FP_COLUMNS].mean()
        fp_std = df[self.FP_COLUMNS].std()

        summary = {
            'metadata': metadata,
            'generated_at': datetime.now().isoformat(),
            'warnings': warnings,
            'statistics': {
                'n_respondents': len(df),
                'fp_averages': fp_means.to_dict(),
                'fp_std': fp_std.to_dict(),
                'fp_min': df[self.FP_COLUMNS].min().to_dict(),
                'fp_max': df[self.FP_COLUMNS].max().to_dict()
            },
            'insights': {
                'top_strength': {
                    'fp': fp_means.idxmax(),
                    'name': self.FP_LABELS[fp_means.idxmax()],
                    'average': round(fp_means.max(), 2)
                },
                'development_area': {
                    'fp': fp_means.idxmin(),
                    'name': self.FP_LABELS[fp_means.idxmin()],
                    'average': round(fp_means.min(), 2)
                }
            },
            'recommendations': self.generate_recommendations(fp_means.to_dict()),
            'individual_profiles': []
        }

        # Add individual profiles
        for _, row in df.iterrows():
            fp_scores = {fp: int(row[fp]) for fp in self.FP_COLUMNS}
            profile = {
                'user_id': row['user_id'],
                'fp_scores': fp_scores,
                'dominant_fp': max(fp_scores, key=fp_scores.get),
                'development_area': min(fp_scores, key=fp_scores.get)
            }
            summary['individual_profiles'].append(profile)

        return summary


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Generate NEP Readiness Dashboard from JSON input',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
    python nep_dashboard_generator.py input.json
    python nep_dashboard_generator.py input.json --output-dir ./reports

Input JSON format:
{
    "school_branch": {"name": "ABC School - Main Branch", "id": "branch_001"},
    "user_type": "teacher",
    "assessment_date": "2026-01-15",
    "responses": [
        {"user_id": "T001", "Q1": "A", "Q2": "B", ..., "Q15": "C"},
        ...
    ]
}
        """
    )

    parser.add_argument('input_file', help='Path to JSON input file')
    parser.add_argument('--output-dir', '-o', default='./output',
                       help='Output directory for generated files (default: ./output)')

    args = parser.parse_args()

    # Load JSON input
    try:
        with open(args.input_file, 'r') as f:
            json_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Input file '{args.input_file}' not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in input file: {e}")
        sys.exit(1)

    # Generate dashboard
    generator = NEPDashboardGenerator()
    result = generator.generate_dashboard(json_data, args.output_dir)

    if result['success']:
        print("Dashboard generated successfully!")
        print(f"\nGenerated files:")
        for name, path in result['files'].items():
            print(f"  - {name}: {path}")

        if result['warnings']:
            print(f"\nWarnings:")
            for warning in result['warnings']:
                print(f"  - {warning}")

        print(f"\nSummary:")
        summary = result['summary']
        print(f"  Respondents: {summary['statistics']['n_respondents']}")
        print(f"  Top Strength: {summary['insights']['top_strength']['name']} ({summary['insights']['top_strength']['average']:.1f})")
        print(f"  Development Area: {summary['insights']['development_area']['name']} ({summary['insights']['development_area']['average']:.1f})")
    else:
        print("Error: Failed to generate dashboard")
        for error in result['errors']:
            print(f"  - {error}")
        sys.exit(1)


if __name__ == '__main__':
    main()
