import curses
from . import slurm_list, slurm_viz, styles

def update_views(stdscr, instance, filter):
    if instance.jobs is None or instance.inf is None:
        return

    instance.rens = slurm_list.view_list(instance, instance.jobs, filter, stylefn=styles.crsstyler, width=instance.left_width if hasattr(instance, 'left_width') else 72, jit=instance.job_id_type if hasattr(instance, 'job_id_type') else 'agg')
    instance.timeme(f"- print job list")

    instance.nocc = slurm_viz.view_viz(instance.inf, instance.jobs, stylefn=styles.crsstyler, mode=instance.view_mode if hasattr(instance, 'view_mode') else 'gpu')
    instance.timeme(f"- view nodeocc")