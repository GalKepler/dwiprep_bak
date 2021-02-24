function cat_apply_deformation(field_file,in_file,interp)
%-----------------------------------------------------------------------
% Job saved on 24-Feb-2021 13:14:09 by cfg_util (rev $Rev: 7345 $)
% spm SPM - SPM12 (7771)
% cfg_basicio BasicIO - Unknown
%-----------------------------------------------------------------------

spm('defaults', 'fmri');
spm_jobman('initcfg');
% matlabbatch{1}.spm.tools.cat.tools.defs2.field = {char(field_file+",1")};
% matlabbatch{1}.spm.tools.cat.tools.defs2.images = {{char(in_file+",1")}};
% matlabbatch{1}.spm.tools.cat.tools.defs2.interp = double(interp);
% matlabbatch{1}.spm.tools.cat.tools.defs2.modulate = 0;
matlabbatch{1}.spm.tools.cat.tools.defs.field1 = {char(field_file+",1")};
matlabbatch{1}.spm.tools.cat.tools.defs.images = {char(in_file+",1")};
matlabbatch{1}.spm.tools.cat.tools.defs.interp = double(interp);
matlabbatch{1}.spm.tools.cat.tools.defs.modulate = 0;
spm_jobman('run', matlabbatch);
end