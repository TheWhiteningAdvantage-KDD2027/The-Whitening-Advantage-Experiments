---
status: PARKED — do not apply
trigger: acceptance notification
target: articleB_whitening_v87.tex and figures/fig11_validity_map.png
---

<<< RECHERCHER
~~~~~~~~~latex
\caption{\textbf{Empirical validity map of the whitening property} ($100$ streams per configuration). \textbf{(A)} $\Gamma$-insensitivity holds past the loss of the fourth moment ($\Gamma \approx 41.6$). \textbf{(B)} Shifted threshold ($c>0$) or continuous MSE loss breaks whitening, mapping the boundaries of Remark~\ref{rem:scope}.}
~~~~~~~~~
=== REMPLACER PAR >>>
~~~~~~~~~latex
\caption{\textbf{Empirical validity map of the whitening property} ($100$ paired streams per configuration, effective sample size $405$). \textbf{(A)} $\Gamma$-insensitivity holds past the loss of the fourth moment ($\Gamma \approx 41.58$). \textbf{(B)} Shifted threshold ($c>0$) or continuous MSE loss breaks whitening, mapping the boundaries of Remark~\ref{rem:scope}.}
~~~~~~~~~
>>> FIN DU BLOC

### Action requise pour les figures :
Remplacer le fichier binaire `figures/Fig11_Whitening_Boundary.png` par l'artefact généré `results/R06_validity_map/figures/fig06_validity_map.png`.

**Justification :** La figure soumise plaçait une graduation d'axe à la frontière analytique du quatrième moment en superposant le marqueur `Γ = 41`, induisant visuellement en erreur quant à la localisation de la mesure. La nouvelle figure sépare la grille des graduations et place la frontière sur sa propre règle isolée.